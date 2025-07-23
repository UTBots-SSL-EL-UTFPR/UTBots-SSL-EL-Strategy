# event_manager.py

from collections import defaultdict
from typing import Callable, Dict, List
from enum import Enum
from core.Field import RobotID

#----------------------------------------------------------------------------#
#                    Class enum para definir possiveis eventos               #
#----------------------------------------------------------------------------#
class EventType(Enum):
    ROBOT_STUCK = "robot_stuck"
    BALL_POSSESSION_CHANGE = "ball_possession_change"
    TARGET_REACHED = "target_reached"
    GOAL_OPEN = "goal_open"
    ENTERED_ZONE = "entered_zone"
    COLLISION_DETECTED = "collision_detected"
    PASS_RECEIVED = "pass_received"
    ...

#----------------------------------------------------------------------------#
#                  Class Event_Manager implementa observer                   #
#----------------------------------------------------------------------------#
class Event_Manager:
    """
    Event_Manager Singleton: sistema de publicação e assinatura de eventos.

    Permite que diferentes partes do sistema se comuniquem de forma desacoplada
    através de eventos nomeados.
    """

    _subscribers: Dict[str, List[Callable]] = defaultdict(list)

    @staticmethod
    def subscribe(event_name: str, callback: Callable):
        """
        Registra um callback para um evento específico.

        :param event_name: Nome do evento (ex: 'robot_stuck')
        :param callback: Função chamada com os dados do evento
        """
        Event_Manager._subscribers[event_name].append(callback)

    @staticmethod
    def publish(event_name: str, **kwargs):
        """
        Dispara o evento para todos os callbacks registrados.

        :param event_name: Nome do evento
        :param kwargs: Dados adicionais passados aos callbacks
        """
        for callback in Event_Manager._subscribers.get(event_name, []):
            callback(**kwargs)

    @staticmethod
    def clear(event_name: str = ""):
        """
        Remove todos os inscritos de um evento ou de todos.

        :param event_name: Nome do evento a limpar (ou todos se None)
        """
        if event_name:
            Event_Manager._subscribers[event_name].clear()
        else:
            Event_Manager._subscribers.clear()

#----------------------------------------------------------------------------#
#                  Class Event_Manager implementa observer                   #
#----------------------------------------------------------------------------#