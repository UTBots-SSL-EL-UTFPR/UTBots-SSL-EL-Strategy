from abc import ABC, abstractmethod

from SSL_configuration.configuration import Configuration

from ..core.World_State import World_State


class Manager(ABC):
    _instance = None
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.configuration = Configuration.getObject()
        self.world_state = World_State.get_object()

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def createEvent(self, name, value):
        # TODO
        pass
