# wall subtree.py

# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #
import py_trees
import math

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers import defense_helpers
from Behaviour_tree.core.World_State import World_State

from utils.defines import ROBOT_RADIUS
from utils.pose2D import ZoneType, Pose2D, RoleType
from Behaviour_tree.commom_behaviours import actions as cb_actions, condition as cb_condition

# -------------------------------------------------------------------------- #
#                           CONSTANTES E CONFIGURAÇÃO                          #
# -------------------------------------------------------------------------- #


THREAT_DISTANCE_ENTER = 1200.0  # mm: quando entra na "zona de ameaça"
THREAT_DISTANCE_EXIT = 1400.0   # mm: quando sai na "zona de ameaça"
MIN_VIS_ANGLE = 0.20            # rad: a visibilidade mínima do gol para ser considerado uma ameaça
MIN_WALL = 1                    
MAX_WALL = 2
VIS_ANGLE_FOR_2 = 0.35
WALL_FACTOR = 0.25              # fração da distância do oponente->gol para posicionar a parede
MIN_WALL_DIST = 200.0
MAX_WALL_DIST = 1000.0

# +------------------------------------------------------------------------+ #
# |                         DEFINIÇÃO DE CONDIÇÕES                             | #
# +------------------------------------------------------------------------+ #

class IsThreateningFoe(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "IsThreateningFoe", threat_distance=1200, min_vis_angle=0.2):
        super().__init__(name)
        self.robot = robot
        self.threat_distance = threat_distance
        self.min_vis_angle = min_vis_angle

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        gk_zone = ZoneType.TEAM_GOALKEEPER.value
        ball = ws.get_ball_position()
        goal_center = FieldHelper.get_team_goal_center()

        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"
        prev_active = getattr(bb, prefix + "active", False)

        is_threat, primary_foe, vis, new_active = defense_helpers.analyze_threatening_foe(
            ws,
            gk_zone,
            ball,
            goal_center,
            prev_wall_active=prev_active,
            threat_distance_enter=self.threat_distance,
            threat_distance_exit=THREAT_DISTANCE_EXIT,
            min_vis_angle=self.min_vis_angle,
        )

        setattr(bb, prefix + "active", new_active)

        if new_active and primary_foe is not None:
            setattr(bb, prefix + "primary_foe", primary_foe)
            setattr(bb, prefix + "vis_angle", vis)
        else:

            if hasattr(bb, prefix + "primary_foe"):
                delattr(bb, prefix + "primary_foe")
            if hasattr(bb, prefix + "vis_angle"):
                delattr(bb, prefix + "vis_angle")

        if is_threat:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE    


class IsRobotAssignedToWall(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "IsRobotAssignedToWall"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        selected_ids = getattr(bb, prefix + "selected_ids", None)
        if selected_ids is None:
            return py_trees.common.Status.FAILURE

        if getattr(self.robot, 'robot_id', None) in selected_ids:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


# +------------------------------------------------------------------------+ #
# |                         DEFINIÇÃO DE AÇÕES                             | #
# +------------------------------------------------------------------------+ #

class CalculateWallParameters(py_trees.behaviour.Behaviour):
    """Compute wall center, size and which robots should form the wall. Write results to the blackboard.

    This node now re-uses the goalkeeper-bisector placement logic so wall geometry matches the GK logic.
    """
    def __init__(self, robot: Bob, name: str = "CalculateWallParameters"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        # Use unified parameter calculation for main wall
        wall_params = defense_helpers.calculate_unified_wall_parameters(
            self.robot.robot_id, wall_type="main"
        )
        
        if not wall_params:
            # Clear blackboard on failure
            for k in ("center_x", "center_y", "perp_dx", "perp_dy", "spacing", "n_wall", "selected_ids", "offsets"):
                if hasattr(bb, prefix + k):
                    delattr(bb, prefix + k)
            return py_trees.common.Status.FAILURE

        # Write results to blackboard
        for key, value in wall_params.items():
            setattr(bb, prefix + key, value)

        return py_trees.common.Status.SUCCESS


class PositionWallRobot(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "PositionWallRobot"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        center_x = getattr(bb, prefix + "center_x", None)
        center_y = getattr(bb, prefix + "center_y", None)
        perp_dx = getattr(bb, prefix + "perp_dx", None)
        perp_dy = getattr(bb, prefix + "perp_dy", None)
        spacing = getattr(bb, prefix + "spacing", None)
        selected_ids = getattr(bb, prefix + "selected_ids", None)

        if None in (center_x, center_y, perp_dx, perp_dy, spacing, selected_ids):
            return py_trees.common.Status.FAILURE

        my_id = getattr(self.robot, 'robot_id', None)
        if my_id not in selected_ids:
            return py_trees.common.Status.FAILURE

        idx = selected_ids.index(my_id)
        offsets = getattr(bb, prefix + "offsets", None)
        if offsets is not None and idx < len(offsets):
            offset = offsets[idx]
        else:
            # For single robot wall, always use zero offset (center position)
            offset = 0.0
        
        # Calculate initial target position
        target_x = center_x + perp_dx * offset
        target_y = center_y + perp_dy * offset
        target = Pose2D(target_x, target_y, 0)

        # Apply goalkeeper-style positioning constraints
        ball = ws.get_ball_position()
        if ball is not None:
            target = defense_helpers.apply_wall_positioning_constraints(target, ball)
        else:
            # Fallback constraint application without ball reference
            target = defense_helpers.clamp_out_goalkeeper_area(target)

        # Path planning integration (inspired by goalkeeper path planning)
        try:
            from Behaviour_tree.helpers.motion_helper import MotionHelper
            
            # Get obstacle positions (similar to goalkeeper obstacle avoidance)
            obstacles = ws.get_all_robot_position()
            # Remove self from obstacles
            current_pos = getattr(self.robot.state, 'position', self.robot.pose)
            obstacles = [obs for obs in obstacles if obs != current_pos]
            
            # Generate optimal path to target
            self.robot.state.target_position = target
            new_path = MotionHelper.find_shortest_path(
                current_pos,
                target,
                obstacles,
                ball,
            )
            self.robot.set_path(new_path)
            
        except (ImportError, AttributeError):
            # Fallback to direct movement if path planning unavailable
            self.robot.set_new_target(target)
            
        # Use appropriate movement type
        self.robot.fast_movement()
        return py_trees.common.Status.SUCCESS

# =========================================================================== #
# ====================== CRIAÇÃO DA ÁRVORE DE BARREIRA ====================== #
# =========================================================================== #


def get_wall_subtree(robot: Bob) -> py_trees.composites.Sequence:

    foes_have_ball = cb_condition.FoesHaveBall(robot)
    is_threatening_foe = IsThreateningFoe(robot)

    calculate_params = CalculateWallParameters(robot)

    is_assigned = IsRobotAssignedToWall(robot)

    position_wall_node = PositionWallRobot(robot)
    move_node = cb_actions.Move_node(robot)

    wall_sequence = py_trees.composites.Sequence(
        "Form Wall Sequence",
        memory=True, 
        children=[
            foes_have_ball,
            is_threatening_foe,
            calculate_params,
            is_assigned,
            position_wall_node,
            move_node,
        ],
    )
    wall_root = py_trees.trees.BehaviourTree(wall_sequence)
    wall_root.setup()
    return wall_root



