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
class PivoAtk(py_trees.behaviour.Behaviour):
    """
    Atualiza a posição de suporte ofensivo do robô, mas apenas se um
    determinado tempo (delta_t) tiver passado desde a última atualização.
    """

    def __init__(
        self,
        path: str,
        name: str = "reposicionar-se como PIVO",
        delta_t: float = 0.5,
    ):
        super().__init__(name)
        self.path = path
        self.delta_t = delta_t
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        robot: Bob = self._bb.get(self.path)
        current_time = time.time()
        new_pos = StrategyHelper.calculate_attack_support_pos(robot.state.position)
        new_path = StrategyHelper.get_Robot_path(
            new_pos, robot.state.position, None
        )
        robot.set_path(new_path)

        self.last_target = new_path[-1]
        self._last_update_time = current_time

    def update(self) -> py_trees.common.Status:
        """
        Verifica o tempo e atualiza a posição se o delta_t foi atingido.
        """
        robot: Bob = self._bb.get(self.path)
        current_time = time.time()
        if self._bb.get(BlackboardKeys.FOES_HAVE_BALL):
            return py_trees.common.Status.FAILURE

        if (current_time - self._last_update_time) > self.delta_t:
            new_pos = StrategyHelper.calculate_attack_support_pos(
                robot.state.position
            )
            new_path = StrategyHelper.get_Robot_path(
                new_pos, robot.state.position, None
            )
            robot.set_path(new_path)
            self.last_target = new_path[-1]
            self._last_update_time = current_time
            logger.debug(new_path)
            return py_trees.common.Status.SUCCESS

        robot.fast_movement()
        robot.state.current_command = self.name
        logger.debug(f"{self.name} - {robot.robot_id.name} - Running")
        return py_trees.common.Status.RUNNING


class PivoDef(py_trees.behaviour.Behaviour):
    """
    Atualiza a posição de suporte ofensivo do robô, mas apenas se um
    determinado tempo (delta_t) tiver passado desde a última atualização.
    """

    def __init__(
        self,
        path: str,
        name: str = "pivo defesa",
        delta_t: float = 0.5,
    ):
        super().__init__(name)
        self.path = path
        self.delta_t = delta_t
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        robot: Bob = self._bb.get(self.path)
        current_time = time.time()
        new_pos = StrategyHelper.calculate_defense_support_pos()
        new_path = StrategyHelper.get_Robot_path(
            new_pos, robot.state.position, None
        )
        robot.set_path(new_path)

        self.last_target = new_path[-1]
        self._last_update_time = current_time

    def update(self) -> py_trees.common.Status:
        """
        Verifica o tempo e atualiza a posição se o delta_t foi atingido.
        """
        robot: Bob = self._bb.get(self.path)
        current_time = time.time()
        if self._bb.get(BlackboardKeys.TEAM_HAS_BALL):
            return py_trees.common.Status.FAILURE

        if (current_time - self._last_update_time) > self.delta_t:
            new_pos = StrategyHelper.calculate_defense_support_pos()
            new_path = StrategyHelper.get_Robot_path(
                new_pos, robot.state.position, None
            )
            robot.set_path(new_path)
            self.last_target = new_path[-1]
            self._last_update_time = current_time
            logger.debug("new target", new_path)
            return py_trees.common.Status.SUCCESS

        logger.debug(f"{self.name} - {robot.robot_id.name} - RUNNING")

        robot.fast_movement()
        return py_trees.common.Status.RUNNING


def get_pivo_tree(path) -> py_trees.trees.BehaviourTree:
    """retorna a root da arvore de comportamento do papel suporte ofensivo
        ela é composta por 3 sub-arvores, sendo elas chute/passe; contestar
        a bola; reposicionar-se.

    :param Bob robot: robo em que essa arvore atua
    """
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    kick_node = cb.get_kick_subtree(path)
    pass_node = cb.get_pass_subtree(path)
    kick_or_pass_sub_tree = py_trees.composites.Selector(
        "escolha entre chute e passe", True, children=[kick_node, pass_node]
    )
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    posse_aliada = PivoAtk(path)
    posse_inimiga = PivoDef(path)
    receber_passe = cb.actions.Receive_pass(path)
    reposition_sub_tree = py_trees.composites.Selector(
        "reposicionar-se",
        True,
        children=[receber_passe, posse_inimiga, posse_aliada],
    )
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    contest_ball_sub_tree = cb.get_luta_pela_bola_sub_tree(path)
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    suporte_off = py_trees.composites.Selector(
        "off sup subtree",
        memory=True,
        children=[
            kick_or_pass_sub_tree,
            reposition_sub_tree,
            contest_ball_sub_tree,
        ],
    )

    root = py_trees.trees.BehaviourTree(suporte_off)
    root.setup()

    return root
