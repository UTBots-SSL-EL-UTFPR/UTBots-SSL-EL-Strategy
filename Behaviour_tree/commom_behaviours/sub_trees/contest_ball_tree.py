# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging
import time

import py_trees

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
        path: str,
        name: str = "PressureOpponent",
        delta_t: float = 0.5,
    ):
        super().__init__(name)
        self.path = path
        self.delta_t = delta_t
        self.last_target = Pose2D(0, 0)
        self._last_update_time = 0.0
        self.foes_with_ball = f"{BlackboardKeys.FOES_HAVE_BALL}"

        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        robot: Bob = _bb.get(self.path)
        current_time = time.time()
        new_pos = StrategyHelper.get_press_oponent_position()
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
        robot: Bob = _bb.get(self.path)
        if not _bb.get(self.foes_with_ball):
            logger.debug(f"{self.name} - FAILURE FOES SEM BOLA")
            return py_trees.common.Status.FAILURE
        current_time = time.time()

        if (current_time - self._last_update_time) > self.delta_t:
            new_pos = StrategyHelper.get_press_oponent_position()
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


def get_luta_pela_bola_sub_tree(path: str) -> py_trees.composites.Selector:
    press_op = PressureOpponent(path)
    rec_bola = RecuperarBola(path)
    onde_ir = py_trees.composites.Selector(
        "onde ir", True, children=[press_op, rec_bola]
    )
    return onde_ir
