from ..core.World_State import World_State, RobotID
from ..core.blackboard import Blackboard_Manager
from ..core import event_callbacks

from utils.pose2D import Pose2D
from utils import utilsp
from utils.defines import Quadrant, QuadrantType, Zone, ZoneType, RoleType, BALL_POSSESSION_DISTANCE

from Behaviour_tree.positioning.positioning_helper import Positioning_helper

from bob import Bob, ROBOT_RADIUS, FREE_DISTANCE
from robot import bob

from SSL_configuration.configuration import Configuration

class Foes_State:
    #ESTADO SIMPLIFICADO DOS ROBOS INIMIGOS

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id

        self.world_state = World_State.get_object()
        self.configuration = Configuration.getObject()
        self.pos_helper = Positioning_helper.get_object()

        self.position: Pose2D = Pose2D(3333, 3333)
        self.velocity: Pose2D = Pose2D()

# ===== provavelmente desnecessario (usado para testes) =====
        self.target_position: Pose2D | None = Pose2D()
        self.active_function = None
        self.current_command = None
        self.role: RoleType | None = None
# ============================================================
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

    def update(self):
        self.update_velocity()
        self.is_ball_with_robot()
        self.is_robot_stuck()
        self.is_visible_from_ball()
        self.is_ball_reachable()

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
        self.current_command = None
        self.has_ball = False
        self.quadrant_index = None
        self.role = None
        self.setup_callbacks()

    # =================== Updates ===================
    def update_velocity(self):       
        new_vel = self.world_state.get_team_robot_velocity(self.robot_id.value)
        if new_vel is not None:
            self.velocity = new_vel
            return 0
        return -1
            

    def update_position(self):
        new_pos = self.world_state.get_team_robot_pose(self.robot_id.value)
        if new_pos is not None:
            self.position = new_pos
            return 0
        return -1

    # =================== Métricas / consultas ===================
    def check_ball_possession(self) -> bool:
        ball_position = self.world_state.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE
        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False
    
    def is_robot_stuck(self):
                #################   Verifica se preso na mesma pos e verifica quadrante   #################
        new_pos = self.world_state.get_team_robot_pose(self.robot_id.value)
        if new_pos is None:
            return

        if self.position == new_pos:
            self.position_rept += 1
        else:
            self.position_rept = 0
            #---------------------quadrante---------------------#
            if new_pos.quadrant != self.position.quadrant:
                event_callbacks.new_quadrant(self.robot_id.name, new_pos.quadrant)
                if new_pos.quadrant != self.position.zone:
                    event_callbacks.new_zone(self.robot_id.name, new_pos.zone)
            self.position = new_pos

        if self.position_rept >= 15:
            self.position_rept = 0
            event_callbacks.on_robot_stuck(self.robot_id.name)

    def is_visible_from_ball(self):
        visible, best_position = Positioning_helper.get_clear_pass_position(
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

    def is_ball_with_robot(self):
        if self.has_ball != self.check_ball_possession():
            if self.has_ball:
                event_callbacks.lost_ball_posetion(self.robot_id.name)
            else:
                self.ball_visible = True
                event_callbacks.team_got_ball_posetion(self.robot_id.name)
            self.has_ball = not self.has_ball


        ################# Verifica se a existe uma linha de passe #################  

        #primeiro a bola  esta no goleiro 
        if self.robot_id == RobotID(2):
            pos_gol=self.get_position()
            pos_1=World_State.get_team_robot_pose(self,1)
            pos_2=World_State.get_team_robot_pose(self,0)
            
            obstacles = self.world_state.get_all_foes_position()
            
            if(Positioning_helper.is_path_clear(pos_gol,pos_1,obstacles,bob.ROBOT_RADIUS) or Positioning_helper.is_path_clear(pos_gol,pos_2,obstacles,bob.ROBOT_RADIUS)):
                event_callbacks.on_valid_line(self.robot_id.name)
        #se a bola esta com outro robo
        elif self.robot_id == RobotID(1):
            pos_1=self.get_position()
            pos_2=World_State.get_team_robot_pose(self,0)
        
            
            obstacles =self.world_state.get_all_foes_position()
             
            if(Positioning_helper.is_path_clear(pos_1,pos_2,obstacles,bob.ROBOT_RADIUS)):
                event_callbacks.on_valid_line(self.robot_id.name)

        else:
            pos_1=self.get_position()
            pos_2=World_State.get_team_robot_pose(self,1)
        
            
            obstacles = self.world_state.get_all_foes_position()
             
            if(Positioning_helper.is_path_clear(pos_1,pos_2,obstacles,bob.ROBOT_RADIUS)):
                event_callbacks.on_valid_line(self.robot_id.name)


        #################   Verifica se preso na mesma pos e verifica quadrante   #################
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

        if self.position_rept >= 15:
            self.position_rept = 0
            event_callbacks.on_robot_stuck(self.robot_id.name)
    # =================== Getters simples para agregador ===================
    def get_position(self)-> Pose2D:
        return self.position

    def get_velocity(self)-> Pose2D:
        return self.velocity

    
    