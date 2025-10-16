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

from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import (
    IsThreateningFoe, IsRobotAssignedToWall, PositionWallRobot
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

        
        wall_params = defense_helpers.calculate_unified_wall_parameters(
            self.robot.robot_id, wall_type="aux"
        )
        
        if not wall_params:
        
            for k in ("center_x", "center_y", "perp_dx", "perp_dy", "spacing", "n_wall", "selected_ids", "offsets"):
                if hasattr(bb, prefix + k):
                    delattr(bb, prefix + k)
            return py_trees.common.Status.FAILURE

  
        for key, value in wall_params.items():
            setattr(bb, prefix + key, value)

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

    position_wall_node = PositionWallRobot(robot)

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