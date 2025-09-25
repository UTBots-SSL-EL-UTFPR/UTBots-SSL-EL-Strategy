# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging
import time
from typing import Optional

import py_trees
from core.blackboard import Blackboard_Manager
from core.event_callbacks import BB_flags_and_values
from robot.bob import Bob

ball_flags = BB_flags_and_values.Flags.motion.ball
positions_values = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()

logger = logging.getLogger(__name__)


class IsInTaskPosition(py_trees.behaviour.Behaviour):
    """Verifica se o robo esta com posicionamento adequado para o papel que desempenha"""

    pass


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
        self.ball_reachable_str = (
            f"{robot.robot_id.name}{BB_flags_and_values.Flags.motion.ball.ball_visible}"
        )

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """decide se irá tentar segurar o passe ou fazer pressão

        :return py_trees.common.Status: Falha se a distancia é grande demais para precionar o oponente, Sucesso se não for
        """
        if not _bb.get(self.ball_reachable_str):
            logger.debug("não estou proximo o suficiente para press oponente")
            return py_trees.common.Status.FAILURE

        return py_trees.common.Status.SUCCESS


# ---------- Actions ----------
class InterceptBall(py_trees.behaviour.Behaviour):
    """
    Executa trajetória de interceptação (chegar no ponto futuro da bola).
    """

    def __init__(self, name: str = "InterceptBall", speed: float = 1.0):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()
        self.speed = speed
        self._start_t: float = 0.0

    def initialise(self) -> None:
        """Marca tempo de início para timeouts, se quiser."""
        self._start_t = time.time()

    def update(self) -> py_trees.common.Status:
        """
        :returns: RUNNING enquanto move; SUCCESS se tocou/segurou a bola; FAILURE em erro/timeout.
        """
        # TODO: chamar seu planner: move_to(self.bb.get(BBKeys.TARGET_POINT))
        # TODO: condição de "tocou bola / travou bola"
        gained = False  # substitua por sensor real
        if gained:
            self.bb.set(BBKeys.HAVE_POSSESSION, True)
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING


class PressureAndBlock(py_trees.behaviour.Behaviour):
    """
    Pressiona o portador: fecha ângulo de chute e tenta o desarme por 'sombra de contato'.
    """

    def __init__(self, name: str = "PressureAndBlock"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        """
        :returns: RUNNING enquanto pressiona; SUCCESS se recuperou posse; FAILURE em erro/timeout.
        """
        # TODO: gerar ponto no arco entre bola e nosso gol; manter distância-ótima e inverter lateral se necessário
        recovered = False  # detector de recuperação
        if recovered:
            self.bb.set(BBKeys.HAVE_POSSESSION, True)
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING
