from typing import List
from ..core.blackboard import Blackboard_Manager
from .Observer import EventClass
from .Observer import Observer

class EventNotifier:
    _instance = None

    def __init__(self):
        if EventNotifier._instance is not None:
            raise Exception("Use EventNotifier.get_instance()")
        EventNotifier._instance = self  # <-- registra a instância única

        self.blackBoard: Blackboard_Manager = Blackboard_Manager.get_instance()
        self._observersList: List[Observer] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()   # <-- salva na variável de classe
        return cls._instance

    
    def removeObserver(self, observer: Observer):
        if observer in self._observersList:
            self._observersList.remove(observer)

 
    def subscribe(self, observer: Observer):
        if not isinstance(observer, Observer):
            raise Exception("Send the fkn right param type, it must to be an Observer instance")
        
        if observer in self._observersList:
            raise Exception("The observer is already subscribed")
        self._observersList.append(observer)

    def reciveEvent(self, event: EventClass):
        if not isinstance(event, EventClass):
            raise Exception("Send the fkn right param type, it must to be an EventEnum instance")

        self.notify(event)
        self.blackBoard.set(event.name, event.value)

    def notify(self, event: EventClass):
        if not isinstance(event, EventClass):
            raise Exception("Send the fkn right param type, it must to be an EventEnum instance")
        for observer in self._observersList:
            observer.notify(event) 