import py_trees
from helpers.strategy_helper import StrategyHelper

from Behaviour_tree.commom_behaviours import actions, condition
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D


# ----------------------------------------------------------------------------------------------------------------------#
class OffSupRepos(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs: condition.Any) -> None:
        return super().setup(**kwargs)

    def initialise(self) -> None:
        return super().initialise()

    def update(self) -> condition.Status:
        pos = StrategyHelper.set_offensive_suport_position(self.robot)
        return py_trees.common.Status.SUCCESS
