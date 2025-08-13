# event_manager.py

from collections import defaultdict
from typing import Callable, Dict, List

#----------------------------------------------------------------------------#
#                  Class Event_Manager implementa observer                   #
#----------------------------------------------------------------------------#
class Event_Manager:
    _subscribers: Dict[str, List[Callable]] = defaultdict(list)

    @staticmethod
    def subscribe(event_name: str, callback: Callable):
        """
        Registra um callback para um evento 

        :param event_name
        :param callback: estamos inscrevendo a função no evento (nao sei se é o ideal, Villean discordou, ja tava feito, ent ta ai)
        """
        Event_Manager._subscribers[event_name].append(callback)

    @staticmethod
    def publish(event_name: str, **kwargs):
        """
        Dispara o evento para todos os callbacks registrados

        :param event_name: Nome do evento
        :param kwargs: Dados adicionais passados aos callbacks (oq a função vai receber)
        """
        for callback in Event_Manager._subscribers.get(event_name, []):
            callback(**kwargs)

    @staticmethod
    def clear(event_name: str = ""):
        """
        limopa eventos
        
        :param event_name: nome evento apagado, pode ser nulo (limpa tudo)
        """
        if event_name:
            Event_Manager._subscribers[event_name].clear()
        else:
            Event_Manager._subscribers.clear()

#----------------------------------------------------------------------------#
#                  Class Event_Manager implementa observer                   #
#----------------------------------------------------------------------------#