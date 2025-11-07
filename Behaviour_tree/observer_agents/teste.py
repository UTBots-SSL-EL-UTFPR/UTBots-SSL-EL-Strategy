from .EventNotifier import EventNotifier
from .StateMachine import StateMachine
from .StateMachine import EventClass
from .StateMachine import EventEnum
from .StateMachine import BobManager

if __name__ == "__main__":
    ev_not = EventNotifier.get_instance()
    sm = StateMachine()
    #ev_not.reciveEvent(EventClass(EventEnum.HALT, True))
    ev_not.reciveEvent(EventClass(EventEnum.TEAM_HAS_BALL, True))
    ev_not.reciveEvent(EventClass(EventEnum.FOES_HAS_BALL, False))
    #ev_not.reciveEvent(EventClass(EventEnum.STOP, True))

    ev_not.reciveEvent(EventClass(EventEnum.HALT, False))
    
    #ev_not.reciveEvent(EventClass(EventEnum.STOP, False))

    