from abc import ABC, abstractmethod
from ..core.event_callbacks import EventEnum

class Observer(ABC):

    def __init__(self):
        from .EventNotifier import EventNotifier
        instance: EventNotifier = EventNotifier.get_instance()
        instance.subscribe(self)

    @abstractmethod
    def update(self, event: EventEnum):
        #Virtual method to recive notifications from notifier
        pass