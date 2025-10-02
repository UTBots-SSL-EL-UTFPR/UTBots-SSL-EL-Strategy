# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging

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

    def __init__(self, robot: Bob, name: str = "PressureOpponent"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()
        self.robot = robot
        self.foes_with_ball = f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}"

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """se prepara para press oponente"""
        if not _bb.get(self.foes_with_ball):
            logger.debug("os oponentes nao estao com a bola")
            return py_trees.common.Status.FAILURE
        self.robot.state.target_position = StrategyHelper.get_press_oponent_position()
        return py_trees.common.Status.SUCCESS


def get_luta_pela_bola_sub_tree(robot: Bob) -> py_trees.composites.Sequence:
    press_op = PressureOpponent(robot)
    rec_bola = RecuperarBola(robot)
    onde_ir = py_trees.composites.Selector(
        "onde ir", False, children=[press_op, rec_bola]
    )

    mov_unico = MovimentoUnico(robot)
    sequencia_brigar_pela_bola = py_trees.composites.Sequence(
        "brigar pela bola", memory=False, children=[onde_ir, mov_unico]
    )
    return sequencia_brigar_pela_bola
