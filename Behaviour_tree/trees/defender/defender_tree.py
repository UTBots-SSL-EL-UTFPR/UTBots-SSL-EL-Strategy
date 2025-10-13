# Behaviour_tree/trees/defender/defender_tree.py
import py_trees
import math
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from .defender_conditions import IsBallInDefensiveHalf
from .defender_strategy_helper import DefenderStrategyHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper  # <-- import

POSITIONAL_TOLERANCE = 150.0

class SmartMarking(py_trees.behaviour.Behaviour):
    BALL_MOVEMENT_THRESHOLD = 50.0  # mm
    SAFE_DISTANCE = 200.0  # distância mínima da bola em mm

    def __init__(self, robot: Bob, name: str = "Marcação Inteligente"):
        super().__init__(name)
        self.robot = robot
        self._ws = World_State.get_object()
        self._locked_safe_target: Pose2D | None = None
        self._last_ball_pos: Pose2D | None = None

    import py_trees
import math
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from .defender_conditions import IsBallInDefensiveHalf
from .defender_strategy_helper import DefenderStrategyHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper  # <-- import

POSITIONAL_TOLERANCE = 150.0

class SmartMarking(py_trees.behaviour.Behaviour):
    BALL_MOVEMENT_THRESHOLD = 50.0  # mm
    SAFE_DISTANCE = 200.0           # distância mínima da bola em mm

    def __init__(self, robot: Bob, name: str = "Marcação Inteligente"):
        super().__init__(name)
        self.robot = robot
        self._ws = World_State.get_object()
        self._last_ball_pos: Pose2D | None = None
        self._locked_safe_target: Pose2D | None = None
        self._using_lateral_step: bool = False  # flag para indicar se está passando pelo desvio

    def update(self) -> py_trees.common.Status:
        current_robot_pose = self._ws.get_team_robot_pose(self.robot.robot_id.value)
        if not current_robot_pose:
            return py_trees.common.Status.FAILURE

        ball_pos = self._ws.get_ball_position()
        if not ball_pos:
            return py_trees.common.Status.FAILURE

        # Ponto final desejado entre bola e nosso gol
        final_target = DefenderStrategyHelper.get_aggressive_marking_pose()
        if not final_target:
            return py_trees.common.Status.FAILURE

        # Recalcula desvio lateral se a bola se moveu muito ou desvio não definido
        if (self._last_ball_pos is None or
            self._last_ball_pos.distance_to(ball_pos) > self.BALL_MOVEMENT_THRESHOLD or
            self._locked_safe_target is None):

            lateral_target = DefenderStrategyHelper.get_safe_target_pose(current_robot_pose)

            # Garante distância mínima da bola
            vec_to_ball = Pose2D(lateral_target.x - ball_pos.x, lateral_target.y - ball_pos.y)
            dist_to_ball = math.hypot(vec_to_ball.x, vec_to_ball.y)
            if dist_to_ball < self.SAFE_DISTANCE:
                if dist_to_ball > 1e-3:
                    scale = self.SAFE_DISTANCE / dist_to_ball
                    lateral_target.x = ball_pos.x + vec_to_ball.x * scale
                    lateral_target.y = ball_pos.y + vec_to_ball.y * scale
                else:
                    lateral_target.x = ball_pos.x + self.SAFE_DISTANCE
                    lateral_target.y = ball_pos.y

            self._locked_safe_target = lateral_target
            self._last_ball_pos = Pose2D(ball_pos.x, ball_pos.y)
            self._using_lateral_step = False

        # Define o alvo real
        target_to_move = final_target

        # Se houver obstáculo, primeiro passa pelo desvio lateral
        obstacle_in_path = not PositioningHelper.is_between_points_with_obstacle(
            point=final_target,
            start=ball_pos,
            end=final_target,
            obstacle=ball_pos,
            tolerance=self.SAFE_DISTANCE
        )

        if obstacle_in_path and not self._using_lateral_step:
            # Passo intermediário pelo desvio lateral
            target_to_move = self._locked_safe_target
            # Se chegar no lateral, seta flag para seguir para final_target
            if current_robot_pose.distance_to(self._locked_safe_target) <= POSITIONAL_TOLERANCE:
                self._using_lateral_step = True
        else:
            target_to_move = final_target

        # Movimenta ou ajusta ângulo
        distance_to_target = current_robot_pose.distance_to(target_to_move)
        if distance_to_target > POSITIONAL_TOLERANCE:
            self.robot.state.target_position = target_to_move
            self.robot.state.current_command = "Aproximando da Posição Segura"
            self.robot.fast_movement()
        else:
            # Rotaciona de frente para a bola
            angle_to_ball = math.atan2(ball_pos.y - current_robot_pose.y,
                                       ball_pos.x - current_robot_pose.x)
            final_angle = Pose2D.normalize_angle_to_pi(angle_to_ball)
            self.robot.state.target_position = Pose2D(current_robot_pose.x,
                                                     current_robot_pose.y,
                                                     final_angle)
            self.robot.state.current_command = "Ajustando Ângulo Frente à Bola"
            error_rad = Pose2D.normalize_angle_to_pi(final_angle - current_robot_pose.theta)
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

def get_defender_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    defensive_branch = py_trees.composites.Sequence(
        "Ramo: Defender",
        memory=False,
        children=[
            IsBallInDefensiveHalf(),
            SmartMarking(robot)
        ]
    )
    base_branch = ReturnToBase(robot)
    root = py_trees.composites.Selector(
        "Comportamento do Defensor",
        memory=False,
        children=[defensive_branch, base_branch]
    )
    return py_trees.trees.BehaviourTree(root)
