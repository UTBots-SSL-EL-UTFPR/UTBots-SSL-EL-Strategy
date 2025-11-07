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


# ----------------------------------------------------------------------------------------------------------------------#
class StopNode(py_trees.behaviour.Behaviour):
    def __init__(
        self,
        robot: Bob,
        name: str = "Parar",
    ):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        super().initialise()

    def update(self) -> Status:
        return py_trees.common.Status.RUNNING


class ExpulsoNode(py_trees.behaviour.Behaviour):
    """
    Atualiza a posição de suporte ofensivo do robô, mas apenas se um
    determinado tempo (delta_t) tiver passado desde a última atualização.
    """

    def __init__(
        self,
        robot: Bob,
        name: str = "sair do campo expulso",
    ):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()
        self.target_reached_key = (
            f"{self.robot.robot_id.name}{BlackboardKeys.TARGET_REACHED}"
        )

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        self._bb.set(self.target_reached_key, False)

        path = StrategyHelper.get_oriented_robot_path(
            Pose2D(0, -1500), self.robot.state.position, 0
        )
        self.robot.set_path(path)
        super().initialise()

    def update(self) -> py_trees.common.Status:
        """
        Verifica o tempo e atualiza a posição se o delta_t foi atingido.
        """
        if bool(self._bb.get(self.target_reached_key)):
            logging.debug(f"{self.name} - {self.robot.robot_id} SUCCESS")
            return py_trees.common.Status.SUCCESS
        logger.debug(f"{self.name} - {self.robot.robot_id.name} - RUNNING")
        self.robot.fast_movement()
        return py_trees.common.Status.RUNNING


def get_expulso_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    """retorna a root da arvore de comportamento do papel suporte ofensivo
        ela é composta por 3 sub-arvores, sendo elas chute/passe; contestar
        a bola; reposicionar-se.

    :param Bob robot: robo em que essa arvore atua
    """
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    expluso = ExpulsoNode(robot)
    stop = StopNode(robot)
    explusoSequence = py_trees.composites.Sequence(
        "sai do campo e para",
        True,
        children=[expluso, stop],
    )

    root = py_trees.trees.BehaviourTree(explusoSequence)
    root.setup()

    return root
