from __future__ import annotations
from abc import ABC, abstractmethod

from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.core.blackboard import Blackboard_Manager

class Behaviour(ABC):
    """
    um 'estado de jogo' dirigido pelo referee.
    nao contem arvores, apenas define permissoes e flags no blackboard.
    """

    def __init__(self, state_name: str) -> None:
        self.ws = World_State.get_object()
        self.bb = Blackboard_Manager.get_instance()
        self.state_name = state_name  # ex: "halt", "stop", "ready_kickoff_us", "running"
        # contrato minimalista de permissoes
        self.permits = {
            "move": False,
            "orient": False,
            "kick": False,
            "place_ball_robot": None,  # id do robo designado, se aplicavel
        }

    def _publish(self) -> None:
        """escreve as flags 'gc_*' no blackboard"""
        self.bb.set("gc_state", self.state_name)
        self.bb.set("gc_can_move", bool(self.permits.get("move", False)))
        self.bb.set("gc_can_kick", bool(self.permits.get("kick", False)))
        #self.bb.set("gc_place_ball_robot", self.permits.get("place_ball_robot"))

    def on_enter(self, prev_state: str | None) -> None:
        """chamado quando este estado se torna ativo"""
        self._publish()

    def on_exit(self, next_state: str | None) -> None:
        """chamado antes de sair deste estado"""
        # opcional: limpar algo especifico do estado
        pass

    @abstractmethod
    def update(self, dt: float = 0.0) -> None:
        """aplicar politica do estado a cada tick e republicar flags se necessario"""
        ...
