import logging
import time

import py_trees

from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.helpers.strategy_helper import StrategyHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------#
class OffSupRepos(py_trees.behaviour.Behaviour):
    """
    Atualiza a posição de suporte ofensivo do robô, mas apenas se um
    determinado tempo (delta_t) tiver passado desde a última atualização.
    """

    def __init__(
        self,
        robot: Bob,
        name: str = "reposicionar-se como sup_off",
        delta_t: float = 2.0,
    ):
        super().__init__(name)
        self.robot = robot
        self.delta_t = delta_t
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        self._last_update_time = 0.1

    def update(self) -> py_trees.common.Status:
        """
        Verifica o tempo e atualiza a posição se o delta_t foi atingido.
        """
        current_time = time.time()

        if (current_time - self._last_update_time) > self.delta_t:
            logger.debug(f"{self.name} - Atualizando posição ({self.name})")
            new_path = StrategyHelper.set_offensive_suport_position(
                self.robot.state.position
            )
            self.robot.set_path(new_path)
            self.last_target = new_path[-1]
            self._last_update_time = current_time
        else:
            logger.debug(
                f"{self.name} usando pos antiga, Aguardando {self.delta_t:.1f}"
            )
            self.robot.set_new_target(self.last_target)
        self.robot.state.current_command = self.name
        return py_trees.common.Status.SUCCESS


def get_off_sup_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    """retorna a root da arvore de comportamento do papel suporte ofensivo
        ela é composta por 3 sub-arvores, sendo elas chute/passe; contestar
        a bola; reposicionar-se.

    :param Bob robot: robo em que essa arvore atua
    """
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    kick_node = cb.get_kick_subtree(robot)
    pass_node = cb.get_pass_subtree(robot)
    kick_or_pass_sub_tree = py_trees.composites.Selector(
        "escolha entre chute e passe", True, children=[kick_node, pass_node]
    )
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    posse_aliada = cb.condition.TeamHasBall()
    receber_passe = cb.actions.Receive_pass(robot)
    pegar_rebote = cb.actions.Rebound_position(robot)
    reposicionar = OffSupRepos(robot)
    reposition_sub_tree = py_trees.composites.Selector(
        "reposicionar-se",
        True,
        children=[receber_passe, pegar_rebote, reposicionar],
    )
    move_node = cb.actions.Move_node(robot)
    go_to_better_position = py_trees.composites.Sequence(
        "escolhe e vai até melhor posicionamento",
        True,
        children=[posse_aliada, reposition_sub_tree, move_node],
    )
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    contest_ball_sub_tree = cb.get_luta_pela_bola_sub_tree(robot)
    # +--------------------------------------------------------------------------+ #
    # +--------------------------------------------------------------------------+ #
    suporte_off = py_trees.composites.Selector(
        "off sup subtree",
        memory=True,
        children=[kick_or_pass_sub_tree, go_to_better_position, contest_ball_sub_tree],
    )

    root = py_trees.trees.BehaviourTree(suporte_off)
    root.setup()

    return root
