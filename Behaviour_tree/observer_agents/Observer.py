from abc import ABC, abstractmethod
from ..core.event_callbacks import Event

class Observer(ABC):

    def __init__(self):
        from .EventNotifier import EventNotifier
        instance: EventNotifier = EventNotifier.get_instance()
        instance.subscribe(self)

    @abstractmethod
    def update(self, event: Event):
        #Virtual method to recive notifications from notifier
        pass