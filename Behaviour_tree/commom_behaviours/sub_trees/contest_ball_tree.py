# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging
import time

import py_trees

from Behaviour_tree.commom_behaviours.actions import MovimentoUnico
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.helpers.strategy_helper import StrategyHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from ..actions import MovimentoUnico, RecuperarBola

_bb = Blackboard_Manager.get_instance()
logger = logging.getLogger(__name__)


class PressureOpponent(py_trees.behaviour.Behaviour):
    """
    decide se o robo deve marcar inimigo
    depende do inimigo estar com a bola
    ja calc uma pos adequada para isso
    é usado quando ja se espera estar em alguma pos entre o inimigo e o gol
    """

    def __init__(
        self,
        robot: Bob,
        name: str = "PressureOpponent",
        delta_t: float = 0.5,
    ):
        super().__init__(name)
        self.robot = robot
        self.delta_t = delta_t
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0
        self.foes_with_ball = f"{BlackboardKeys.FOES_HAVE_BALL}"

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
        if not _bb.get(self.foes_with_ball):
            logger.debug(f"{self.name} - FAILURE FOES SEM BOLA")
            return py_trees.common.Status.FAILURE
        new_pos = StrategyHelper.get_press_oponent_position()
        self.robot.set_new_target_position(new_pos)
        return py_trees.common.Status.SUCCESS


def get_luta_pela_bola_sub_tree(robot: Bob) -> py_trees.composites.Sequence:
    press_op = PressureOpponent(robot)
    rec_bola = RecuperarBola(robot)
    fastMove = MovimentoUnico(robot)
    onde_ir = py_trees.composites.Selector(
        "onde ir", True, children=[press_op, rec_bola]
    )
    mover_rapido = py_trees.composites.Sequence(
        "superNome", False, children=[onde_ir, fastMove]
    )
    return mover_rapido
