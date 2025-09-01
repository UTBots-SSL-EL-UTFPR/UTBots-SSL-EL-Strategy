"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""
from __future__ import annotations
from time import sleep

from Behaviour_tree.core.blackboard import Blackboard_Manager
import time
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from  Behaviour_tree.core import event_callbacks as callbacks
navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions

from Behaviour_tree.robot.bob import Bob
#---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
#---------------------------------------------------------------------------------------#

from typing import Optional, Tuple
import time
import py_trees as pt

class Move_node(pt.behaviour.Behaviour):
    """
    Nó de movimento genérico: empurra o robô  até robot.state.target_position (path inteiro)

    :param name: Nome do nó.
    :type name: str
    :param robot: Instância do robô (Bob).
    :type robot: Bob | None
    :param target_reached_key: Chave do Blackboard que sinaliza 'alvo alcançado' (bool).
                               Ex.: f\"{robot.robot_id.name}{navigation_flags.target_reached}\".
    :type target_reached_key: str
    :param timeout_s: Tempo máximo (segundos) para tentar alcançar o alvo antes de retornar FAILURE.
    :type timeout_s: float
    """

    def __init__(
        self,
        name: str = "MOVE",
        robot = None,
        timeout_s: float = 3.0,
    ):
        super().__init__(name=name)
        self.robot :  Bob | None = robot
        self._bb = Blackboard_Manager.get_instance()

        self.target_reached_key = ""
        self.timeout_s = timeout_s

        self._t0: float = 0.0
        self._last_move_ts: float = 0.0
        self._stall_ticks: int = 0
        self._max_stall_ticks: int = 30 


    def setup(self, **kwargs) -> None:
        """
        Prepara o nó para execução. Registre chaves do BB aqui se sua API suportar.

        :raises RuntimeError: se 'robot' não estiver definido.
        """
        print("setup")
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.target_reached_key = f"{self.robot.robot_id.name}{navigation_flags.target_reached}"

    def initialise(self) -> None:
        """
        Chamado no primeiro tick ativo (ou reentrada). Zera temporais, limpa flags,
        e carrega alvo do BB para o estado do robô se necessário.
        """
        if self.robot is None or self.robot.state is None:
            return
        self._t0 = time.time()
        self._last_move_ts = self._t0
        self._stall_ticks = 0
        self._bb.set(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}", False) # type: ignore
        print(f"{self.robot.robot_id} -> INIT MOVEMENT")

        self._bb.set(self.target_reached_key, False)

    def update(self) -> pt.common.Status:
        """
        Empurra o robô a mover-se (via `robot.move_oriented()`) enquanto não atingiu o alvo.
        Depende do Blackboard para saber se o alvo foi alcançado (`target_reached_key`).

        :returns: SUCCESS quando alvo alcançado; RUNNING durante o deslocamento; FAILURE em erro/timeout.
        :rtype: pt.common.Status
        """
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        if bool(self._bb.get(self.target_reached_key)):
            print(f"{self.robot.robot_id} -> TARGET REACHED")
            return pt.common.Status.SUCCESS

        if not getattr(self.robot.state, "target_position", None):
            return pt.common.Status.FAILURE

        try:
            self.robot.move_oriented() 
        except Exception as exc:
            return pt.common.Status.FAILURE

        if (time.time() - self._t0) > self.timeout_s:
            print(f"{self.robot.robot_id} -> MOVE TIMEOUT")
            return pt.common.Status.FAILURE

        if self._bb.get(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}"):
            print(f"{self.robot.robot_id} -> ROBOT STUCK")
            return pt.common.Status.FAILURE
        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status) -> None:
        """
        Limpa estado local e o alvo do robô. Dispara callback de reset.

        :param new_status: status no qual o nó terminou (SUCCESS/FAILURE/INVALID).
        :type new_status: pt.common.Status
        """
        if self.robot is None or getattr(self.robot, "state", None) is None:
            return

        self.robot.state.target_position = None

        try:
            callbacks.target_reset(self.robot.robot_id.name)
        except Exception:
            pass
