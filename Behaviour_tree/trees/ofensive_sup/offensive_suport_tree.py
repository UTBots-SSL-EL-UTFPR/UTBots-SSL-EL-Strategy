from typing import Callable, Optional, Tuple

import py_trees

from Behaviour_tree.commom_behaviours import actions
from Behaviour_tree.commom_behaviours import condition
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D


# ----------------------------------------------------------------------------------------------------------------------#
class GotPossetion(py_trees.behaviour.Behaviour):
    """
    Curto-circuito: se já temos posse, encerra a subárvore com SUCCESS.
    """

    def __init__(self, robot: Bob, name: str = "AlreadyHavePossession"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        """_summary_

        :return py_trees.common.Status: _description_
        """
        have = bool(
            self.bb.get(f"{self.robot.robot_id.name}{ball_flags.has_ball}") or False
        )
        return (
            py_trees.common.Status.SUCCESS if have else py_trees.common.Status.FAILURE
        )
