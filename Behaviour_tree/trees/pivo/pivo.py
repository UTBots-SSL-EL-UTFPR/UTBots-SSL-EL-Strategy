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
        delta_t: float = 0.6,
    ):
        super().__init__(name)
        self.path = path
        self.last_target = Pose2D(0, 0)
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
        robot: Bob = self._bb.get(self.path)
        current_time = time.time()
        if self._bb.get(BlackboardKeys.FOES_HAVE_BALL) or not self._bb.get(
            BlackboardKeys.TEAM_HAS_BALL
        ):
            return py_trees.common.Status.FAILURE
        new_pos = StrategyHelper.calculate_attack_support_pos(robot.state.position)
        robot.set_new_target_position(new_pos)
        self._last_update_time = current_time
        return py_trees.common.Status.SUCCESS


class PivoDef(py_trees.behaviour.Behaviour):
    """
    Atualiza a posição de suporte ofensivo do robô, mas apenas se um
    determinado tempo (delta_t) tiver passado desde a última atualização.
    """

    def __init__(
        self,
        path: str,
        name: str = "pivo defesa",
    ):
        super().__init__(name)
        self.path = path
        self.last_target = Pose2D(0, 0)
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
        robot: Bob = self._bb.get(self.path)
        if self._bb.get(BlackboardKeys.TEAM_HAS_BALL):
            return py_trees.common.Status.FAILURE or not self._bb.get(
                BlackboardKeys.FOES_HAVE_BALL
            )

        new_pos = StrategyHelper.calculate_defense_support_pos()
        robot.set_new_target_position(new_pos)
        return py_trees.common.Status.SUCCESS


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
    mover = Move_node(path)
    reposition_sub_tree = py_trees.composites.Selector(
        "reposicionar-se",
        True,
        children=[receber_passe, posse_inimiga, posse_aliada],
    )
    reposition_move_tree = py_trees.composites.Sequence(
        "mover", True, children=[reposition_sub_tree, mover]
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
            reposition_move_tree,
            contest_ball_sub_tree,
        ],
    )

    root = py_trees.trees.BehaviourTree(suporte_off)
    root.setup()

    return root
