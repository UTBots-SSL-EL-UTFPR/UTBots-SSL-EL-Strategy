from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from SSL_configuration.configuration import Configuration
from utils.defines import BALL_POSSESSION_DISTANCE
from utils.pose2D import Pose2D, RoleType

from ..core import event_callbacks
from ..core.World_State import TeamID, World_State


class Bob_State:
    """Estado dinâmico do robô (posição, velocidade, posse, quadrante e role)."""

    def __init__(self, robot_id: TeamID):
        self.robot_id = robot_id

        self.world_state = World_State.get_object()
        self.configuration = Configuration.getObject()
        self.pos_helper = PositioningHelper.get_object()

        self.position: Pose2D = Pose2D(3333, 3333)
        self.velocity: Pose2D = Pose2D()

        self.path: list[Pose2D] = []
        self.path_index = 0
        self.target_position: Pose2D | None = Pose2D()
        self.target_theta: float = 0
        self.active_function = None
        self.current_command: str = "None"
        self.role: RoleType | None = None

        self.ball_visible = False
        self.has_ball = False
        self.position_rept = 0

    def setup_callbacks(self):

        event_callbacks.lost_ball_posetion(self.robot_id.name)
        event_callbacks.new_quadrant(self.robot_id.name, 0)
        event_callbacks.new_zone(self.robot_id.name, 0)
        event_callbacks.on_robot_stuck(self.robot_id.name)
        event_callbacks.target_reset(self.robot_id.name)
        event_callbacks.on_ball_not_visible(self.robot_id.name, Pose2D(0, 0))

    # ---------------------------------------------------------------------------------------#
    #                                       UPDATE                                          #
    # temos os seguintes eventos:                                                           #
    #   1. Mudança de posse de bola                                                         #
    #   3. Verifica target_position + repetição de target
    # ---------------------------------------------------------------------------------------#

    def update(self):
        self.is_ball_with_robot()
        self.is_robot_stuck()
        self.target_reached()
        self.is_visible_from_ball()
        self.is_ball_reachable()

    def is_ball_with_robot(self):
        if self.has_ball != self.check_ball_possession():
            if self.has_ball:
                print(self.robot_id)
                event_callbacks.lost_ball_posetion(self.robot_id.name)
            else:
                self.ball_visible = True
                event_callbacks.team_got_ball_posetion(self.robot_id.name)
            self.has_ball = not self.has_ball

    def is_robot_stuck(self):
        new_pos = self.world_state.get_team_robot_pose(self.robot_id.value)
        if new_pos is None:
            return

        if self.position == new_pos:
            self.position_rept += 1
        else:
            self.position_rept = 0
            if new_pos.quadrant != self.position.quadrant:
                event_callbacks.new_quadrant(self.robot_id.name, new_pos.quadrant)
                if new_pos.quadrant != self.position.zone:
                    event_callbacks.new_zone(self.robot_id.name, new_pos.zone)
            self.position = new_pos

        if self.position_rept >= 500:
            self.position_rept = 0
            event_callbacks.on_robot_stuck(self.robot_id.name)

    def target_reached(self):
        """
        Verifica se o robô alcançou o alvo atual no caminho.
        Se o alvo for o último do percurso, limpa o caminho e sinaliza o evento.
        Caso contrário, avança para o próximo alvo do caminho.
        """
        if not self.path:
            return

        self.target_position = self.path[self.path_index]
        if self.target_position.is_in_range(
            self.position, self.configuration.threshould_arrived_target
        ):
            if self.path_index >= len(self.path) - 1:
                self.path.clear()
                self.path_index = 0
                event_callbacks.on_target_reached(self.robot_id.name)
            else:
                self.path_index += 1

    def is_visible_from_ball(self):
        visible, best_position = PositioningHelper.get_clear_pass_position(
            self.position
        )
        if visible != self.ball_visible:
            if visible:
                event_callbacks.on_ball_visible(self.robot_id.name)
            else:
                event_callbacks.on_ball_not_visible(self.robot_id.name, best_position)

        self.ball_visible = visible

    def is_ball_reachable(self):
        reachable = 500 > self.position.distance_to(
            self.world_state.get_ball_position()
        )
        event_callbacks.on_ball_reachable(self.robot_id.name, reachable)

    # ---------------------------------------------------------------------------------------#
    #                                         Setters                                       #
    # ---------------------------------------------------------------------------------------#
    def set_position(self, position: Pose2D):
        """Define manualmente a posição e recalcula quadrante e role."""
        self.position = position
        self.quadrant_index = self.position.quadrant

    def set_velocity(self, velocity: Pose2D):
        """Atualiza o vetor de velocidade (vx, vy)."""
        self.velocity = velocity

    def set_orientation(self, angle: float):
        """Define a orientação atual do robô."""
        self.orientation = angle

    def set_target_position(self, position: Pose2D):
        """Define uma posição alvo (goal) para planejamento de movimento."""
        event_callbacks.target_reset(self.robot_id.name)
        self.target_position = position

    def reset(self):
        """Restaura o estado para valores padrão (limpa alvo, role e quadrante)."""
        self.position = Pose2D()
        self.velocity = Pose2D()
        self.target_position = Pose2D()
        self.active_function = None
        self.current_command = "None"
        self.has_ball = False
        self.quadrant_index = None
        self.role = None
        self.setup_callbacks()

    # ---------------------------------------------------------------------------------------#
    #                                   METRICAS/CONSULTAS                                  #
    # ---------------------------------------------------------------------------------------#
    def check_ball_possession(self) -> bool:
        ball_position = self.world_state.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE
        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False

    # =================== Getters simples para agregador ===================
    def get_position(self) -> Pose2D:
        return self.position

    def get_velocity(self) -> Pose2D:
        return self.velocity

    # =================== Internos de classificação ===================
