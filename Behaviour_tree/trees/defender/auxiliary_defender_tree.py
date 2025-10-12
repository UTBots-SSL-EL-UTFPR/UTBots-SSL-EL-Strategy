import py_trees
import math
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from .defender_strategy_helper import DefenderStrategyHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper

POSITIONAL_TOLERANCE = 150.0
BALL_MOVEMENT_THRESHOLD = 50.0  # mm
SAFE_DISTANCE = 200.0           # distância mínima do alvo em mm


class AuxiliarySmartMarking(py_trees.behaviour.Behaviour):
    """
    O defensor auxiliar marca o adversário mais longe da bola (exceto goleiro),
    posicionando-se na trajetória bola -> adversário, mas o mais próximo possível do adversário.
    """

    def __init__(self, robot: Bob, name: str = "Marcação Auxiliar"):
        super().__init__(name)
        self.robot = robot
        self._ws = World_State.get_object()
        self._locked_safe_target: Pose2D | None = None
        self._last_target_pos: Pose2D | None = None
        self._using_lateral_step: bool = False

    def _get_target_opponent(self) -> Pose2D | None:
        """Retorna o adversário mais longe da bola (excluindo o goleiro)."""
        ball_pos = self._ws.get_ball_position()
        if not ball_pos:
            return None

        # ID do goleiro (menor ID por convenção)
        goalkeeper_id = min(self._ws.configuration.foes_id)

        farthest_foe = None
        max_distance = -1

        for foe_id in self._ws.configuration.foes_id:
            if foe_id == goalkeeper_id:
                continue
            foe_pos = self._ws.get_foe_robot_pose(foe_id)
            if not foe_pos:
                continue

            dist = ball_pos.distance_to(foe_pos)
            if dist > max_distance:
                max_distance = dist
                farthest_foe = foe_pos

        return farthest_foe

    def update(self) -> py_trees.common.Status:
        current_pose = self._ws.get_team_robot_pose(self.robot.robot_id.value)
        if not current_pose:
            return py_trees.common.Status.FAILURE

        target_foe = self._get_target_opponent()
        if not target_foe:
            return py_trees.common.Status.FAILURE

        ball_pos = self._ws.get_ball_position()
        if not ball_pos:
            return py_trees.common.Status.FAILURE

        # Calcula posição na trajetória bola -> adversário, próximo do adversário
        dx = target_foe.x - ball_pos.x
        dy = target_foe.y - ball_pos.y
        fraction = 0.85  # perto do adversário
        mark_target = Pose2D(
            ball_pos.x + dx * fraction,
            ball_pos.y + dy * fraction,
            0.0
        )

        # Garante distância mínima de segurança do adversário
        dist_to_foe = mark_target.distance_to(target_foe)
        if dist_to_foe < SAFE_DISTANCE:
            angle = math.atan2(mark_target.y - target_foe.y, mark_target.x - target_foe.x)
            mark_target.x = target_foe.x + SAFE_DISTANCE * math.cos(angle)
            mark_target.y = target_foe.y + SAFE_DISTANCE * math.sin(angle)

        # Movimenta ou ajusta ângulo
        dist_to_target = current_pose.distance_to(mark_target)
        if dist_to_target > POSITIONAL_TOLERANCE:
            self.robot.state.target_position = mark_target
            self.robot.state.current_command = "Marcando o adversário mais longe da bola"
            self.robot.fast_movement()
        else:
            # Rotaciona de frente para a bola
            angle_to_ball = math.atan2(
                ball_pos.y - current_pose.y,
                ball_pos.x - current_pose.x
            )
            final_angle = Pose2D.normalize_angle_to_pi(angle_to_ball)
            self.robot.state.target_position = Pose2D(
                current_pose.x, current_pose.y, final_angle
            )
            self.robot.state.current_command = "Ajustando Ângulo Frente à Bola"

            error_rad = Pose2D.normalize_angle_to_pi(final_angle - current_pose.theta)
            ANGLE_TOLERANCE = math.radians(5)
            if abs(error_rad) < ANGLE_TOLERANCE:
                self.robot.stop()
                self.robot.state.current_command = "Ângulo Frente à Bola Ajustado"
            else:
                self.robot.rotate()

        return py_trees.common.Status.RUNNING




class ReturnToBase(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Retornar para Base"):
        super().__init__(name)
        self.robot = robot
        self.base_position = DefenderStrategyHelper.get_base_position_by_id(robot.robot_id)

    def update(self) -> py_trees.common.Status:
        self.robot.state.target_position = self.base_position
        self.robot.state.current_command = "Retornando para a Base"
        self.robot.fast_movement()
        return py_trees.common.Status.RUNNING


def get_auxiliary_defender_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    defensive_branch = py_trees.composites.Sequence(
        "Ramo: Defensor Auxiliar",
        memory=False,
        children=[AuxiliarySmartMarking(robot)],
    )

    base_branch = ReturnToBase(robot)

    root = py_trees.composites.Selector(
        "Comportamento do Defensor Auxiliar",
        memory=False,
        children=[defensive_branch, base_branch],
    )

    return py_trees.trees.BehaviourTree(root)
