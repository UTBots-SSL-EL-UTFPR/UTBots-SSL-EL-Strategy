# Halt.py
import logging
import time

import py_trees
from py_trees.common import Status

from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.helpers.strategy_helper import StrategyHelper
from Behaviour_tree.robot.bob import Bob, TeamID
from utils.pose2D import Pose2D

logger = logging.getLogger(__name__)


class StopNode(py_trees.behaviour.Behaviour):
    def __init__(
        self,
        path: str,
        name: str = "Parar",
    ):
        super().__init__(name)
        self.path = path

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        super().initialise()

    def update(self) -> Status:
        return py_trees.common.Status.RUNNING


def get_stop_tree(path: str) -> py_trees.trees.BehaviourTree:
    stop = StopNode(path)
    explusoSequence = py_trees.composites.Sequence(
        "sai do campo e para",
        True,
        children=[stop],
    )

    root = py_trees.trees.BehaviourTree(explusoSequence)
    root.setup()

    return root
