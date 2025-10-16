# aux_wall_subtree.py
# Auxiliary wall behaviour tree that places robots on the best side of the wall mouth.

import py_trees
import math

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.helpers import defense_helpers
from Behaviour_tree.core.World_State import World_State

from utils.defines import ROBOT_RADIUS
from utils.pose2D import Pose2D
from Behaviour_tree.commom_behaviours import actions as cb_actions, condition as cb_condition

# Import shared wall functions and classes
from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import (
    IsThreateningFoe, IsRobotAssignedToWall,
    WALL_FACTOR, MIN_WALL_DIST, MAX_WALL_DIST
)

# +------------------------------------------------------------------------+ #
# |                         DEFINIÇÃO DE AÇÕES                             | #
# +------------------------------------------------------------------------+ #

class AuxWallCalculateParameters(py_trees.behaviour.Behaviour):
    """Calculate wall parameters constrained to the best side of the goal mouth (left or right half).

    This node selects offsets only on the chosen side so the auxiliary wall places robots on one side.
    Enhanced with goalkeeper-inspired adaptive positioning and constraint management.
    """
    def __init__(self, robot: Bob, name: str = "AuxWallCalculateParameters"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        # Use unified parameter calculation for auxiliary wall
        wall_params = defense_helpers.calculate_unified_wall_parameters(
            self.robot.robot_id, wall_type="aux"
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


class AuxWallPositioner(py_trees.behaviour.Behaviour):
    """Position robots for auxiliary wall using unified positioning logic."""
    def __init__(self, robot: Bob, name: str = "AuxWallPositioner"):
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
            # Fallback to center position
            offset = 0.0
        
        # Calculate initial target position
        target_x = center_x + perp_dx * offset
        target_y = center_y + perp_dy * offset
        target = Pose2D(target_x, target_y, 0)

        # Apply shared positioning constraints
        ball = ws.get_ball_position()
        if ball is not None:
            target = defense_helpers.apply_wall_positioning_constraints(target, ball)
        else:
            target = defense_helpers.clamp_out_goalkeeper_area(target)

        # Apply path planning (same as main wall)
        try:
            from Behaviour_tree.helpers.motion_helper import MotionHelper
            
            obstacles = ws.get_all_robot_position()
            current_pos = getattr(self.robot.state, 'position', self.robot.pose)
            obstacles = [obs for obs in obstacles if obs != current_pos]
            
            self.robot.state.target_position = target
            new_path = MotionHelper.find_shortest_path(
                current_pos,
                target,
                obstacles,
                ball,
            )
            self.robot.set_path(new_path)
        except ImportError:
            # Fallback if motion helper not available
            self.robot.state.target_position = target

        return py_trees.common.Status.SUCCESS


# =========================================================================== #
# ================ CRIAÇÃO DA ÁRVORE DE AUXILIAR DE BARREIRA ================ #
# =========================================================================== #

def get_aux_wall_subtree(robot: Bob) -> py_trees.composites.Sequence:
    """Auxiliary wall subtree: places robots on the best side of the wall mouth.

    This function constructs a behaviour tree sequence that mirrors the main wall
    subtree but uses the side-aware AuxWallCalculateParameters node so robots
    are placed on the most threatened side of the goal mouth.
    """
    foes_have_ball = cb_condition.FoesHaveBall(robot)
    is_threatening_foe = IsThreateningFoe(robot)

    calculate_params = AuxWallCalculateParameters(robot)

    is_assigned = IsRobotAssignedToWall(robot)

    # Use auxiliary-specific positioning node that handles triangle-optimized parameters
    position_wall_node = AuxWallPositioner(robot)

    aux_wall_subtree = py_trees.composites.Sequence(
        "Aux Wall Sequence",
        memory=True,
        children=[
            foes_have_ball,
            is_threatening_foe,
            calculate_params,
            is_assigned,
            position_wall_node
        ],
    )
    aux_wall_subtree.setup()
    return aux_wall_subtree