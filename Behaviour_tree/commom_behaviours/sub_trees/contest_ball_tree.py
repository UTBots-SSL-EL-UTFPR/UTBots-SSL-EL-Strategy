# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging
import time
from typing import Optional

import py_trees
from core.blackboard import Blackboard_Manager
from core.event_callbacks import BlackboardKeys
from robot.bob import Bob

ball_flags = BlackboardKeys.Flags.motion.ball
positions_values = BlackboardKeys.Values.Positions
team_flags = BlackboardKeys.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()

logger = logging.getLogger(__name__)


sequence_MarkOpponent = py_trees.composites.Sequence("Mark_opponent", True)
sequence_Fight_for_posetion = py_trees.composites.Sequence("Fight_for_posetion", True)


class Foes_got_ball(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está com adversário (TODO)
    """

    def __init__(self, name: str = "IsBallFree"):
        super().__init__(name)

    def initialise(self) -> None:
        """Reseta/atualiza contexto no início da verificação."""
        ...

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(
            f"{team_flags.Ball_posetion.foes_have_ball}"
        ):  # (TODO) -> update de foes
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class PressureOpponent(py_trees.behaviour.Behaviour):
    """
    decide se irá tentar segurar o passe ou fazer pressão
    """

    def __init__(self, robot: Bob, name: str = "TeammateIsBestToReachBall"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()
        self.foes_with_ball = f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}"

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """decide se irá tentar segurar o passe ou fazer pressão

        :return py_trees.common.Status: Falha se a distancia é grande demais para precionar o oponente, Sucesso se não for
        """
        if not _bb.get():
            logger.debug("não estou proximo o suficiente para press oponente")
            return py_trees.common.Status.FAILURE

        return py_trees.common.Status.SUCCESS
