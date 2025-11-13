import logging
import time

import py_trees

from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.commom_behaviours.actions import Move_node
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.helpers.strategy_helper import StrategyHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------#
class SenhorBarreiraDaSilva(py_trees.behaviour.Behaviour):
    """
    senhor barreira da silva
    """

    def __init__(
        self,
        path: str,
        name: str = "reposicionar-se como Barreira",
    ):
        super().__init__(name)
        self.path = path
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        pass

    def update(self) -> py_trees.common.Status:
        """
        Verifica o tempo e atualiza a posição se o delta_t foi atingido.
        """
        robot = self._bb.get(self.path)
        new_pos = StrategyHelper.get_barreira_position()

        robot.set_new_target_position(new_pos)
        return py_trees.common.Status.SUCCESS


def get_barreira_tree(path: str) -> py_trees.trees.BehaviourTree:
    barreira = SenhorBarreiraDaSilva(path)
    move = Move_node(path)
    arvorebarreira = py_trees.composites.Sequence(
        "arvorebarreira",
        memory=True,
        children=[barreira, move],
    )

    root = py_trees.trees.BehaviourTree(arvorebarreira)
    root.setup()

    return root
