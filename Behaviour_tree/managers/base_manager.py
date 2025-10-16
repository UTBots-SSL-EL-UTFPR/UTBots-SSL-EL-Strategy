from __future__ import annotations
from abc import ABC, abstractmethod

from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.core.blackboard import Blackboard_Manager


class BaseManager(ABC):
    """
    contrato comum para os managers de alto nivel
    fornece acesso ao World_State e Blackboard 
    """
    def __init__(self) -> None:
        self.ws = World_State.get_object()
        self.bb = Blackboard_Manager.get_instance()

    @abstractmethod
    def create(self) -> None:
        ...

    @abstractmethod
    def update(self, dt: float = 0.0) -> None:
        ...
