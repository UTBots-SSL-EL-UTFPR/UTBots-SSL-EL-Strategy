# behaviors/duels/fight_for_ball.py
from __future__ import annotations

import logging
import time
from typing import Optional

import py_trees
from core.blackboard import Blackboard_Manager
from core.event_callbacks import BB_flags_and_values

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

    def __init__(self, name: str = "TeammateIsBestToReachBall", robot_id=""):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()
        self.ball_reachable_str = (
            f"{robot_id}{BB_flags_and_values.Flags.motion.ball.ball_visible}"
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

        # -> definir distancia maxima robo-bola
        # pos helper -> get_press_position
        ...


class GotPossetion(py_trees.behaviour.Behaviour):
    """
    Curto-circuito: se já temos posse, encerra a subárvore com SUCCESS.
    """

    def __init__(self, name: str = "AlreadyHavePossession"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        """_summary_

        :return py_trees.common.Status: _description_
        """
        have = bool(self.bb.get(BBKeys.HAVE_POSSESSION) or False)
        return (
            py_trees.common.Status.SUCCESS if have else py_trees.common.Status.FAILURE
        )


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


class AssistBlockPassingLanes(py_trees.behaviour.Behaviour):
    """
    Se um colega é o melhor para a bola, outro fecha linhas de passe curtas e cria 'screen'.
    """

    def __init__(self, name: str = "AssistBlockPassingLanes"):
        super().__init__(name)
        self.bb = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        """
        :returns: RUNNING enquanto bloqueia; SUCCESS se equipe obteve posse; FAILURE se incoerente.
        """
        # TODO: posicionar-se entre portador e receptores prováveis; micro-ajustes por gradient descent simples
        team_have = bool(self.bb.get(BBKeys.HAVE_POSSESSION) or False)
        return (
            py_trees.common.Status.SUCCESS
            if team_have
            else py_trees.common.Status.RUNNING
        )


# ---------- Montagem da Subárvore ----------
def create_fight_for_ball_subtree(
    name: str = "FightForBall",
) -> py_trees.behaviour.Behaviour:
    """
    Cria a subárvore de 'brigar pela bola'.

    Estrutura (prioridade):
    1) Se já temos posse -> SUCCESS (curto-circuito)
    2) [Bola livre & Eu sou o melhor] -> Intercepta
    3) [Oponente com controle] -> Pressão & Bloqueio
    4) [Colega é o melhor] -> Assistência (fechar linhas)
    5) Fallback -> Compactação

    :param name: Nome do nó raiz desta subárvore.
    :returns: Nó raiz (Selector) pronto para ser plugado na árvore principal.
    """
    root = py_trees.composites.Selector(name=name, memory=True)

    # 1) Curto-circuito
    have = AlreadyHavePossession("HavePossession?")
    root.add_children([have])

    # 2) Bola livre + sou melhor -> intercepta (Sequence)
    seq_intercept = py_trees.composites.Sequence(
        name="FreeBall_Intercept", memory=False
    )
    seq_intercept.add_children(
        [
            IsBallFree("BallFree?"),
            AmIBestToReachBall("AmIBest?"),
            InterceptBall("Intercept"),
        ]
    )
    root.add_children([seq_intercept])

    # 3) Adversário com controle -> pressionar/bloquear (Sequence)
    seq_press = py_trees.composites.Sequence(name="OppControl_Press", memory=False)
    seq_press.add_children(
        [OpponentHasControlNearby("OppHasCtrl?"), PressureAndBlock("Press&Block")]
    )
    root.add_children([seq_press])

    # 4) Colega é melhor -> assistência (Sequence)
    seq_assist = py_trees.composites.Sequence(name="TeammateBest_Assist", memory=False)
    seq_assist.add_children(
        [TeammateIsBestToReachBall("TMisBest?"), AssistBlockPassingLanes("AssistBlock")]
    )
    root.add_children([seq_assist])

    # 5) Fallback
    root.add_children([CompactFallback("CompactFallback")])

    return root
