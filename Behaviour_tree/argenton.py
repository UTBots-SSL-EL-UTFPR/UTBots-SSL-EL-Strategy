import logging
import time
from typing import List

import py_trees

from .core import World_State
from .robot.BobManager import Bob, BobManager, TeamID
from .trees.barreira.Barreira import get_barreira_tree
from .trees.defender.defender_tree import get_defender_tree
from .trees.goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from .trees.ofensive_sup.offensive_suport_tree import get_off_sup_tree
from .trees.pivo.pivo import get_pivo_tree
from .observer_agents.StateMachine import StateMachine
from .observer_agents.EventNotifier import EventNotifier
from .observer_agents.StateMachine import EventClass
from .observer_agents.StateMachine import EventEnum


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class StateMockObj:
    def __init__(self) -> None:
        self.bobManager: BobManager = BobManager.get_instance()
        self.stateMachine = StateMachine()
        self.eventNotifier = EventNotifier.get_instance()

    def update(self, event: EventClass | None = None):
        self.bobManager.update()

        if event is not None:
            self.eventNotifier.reciveEvent(event)

        self.stateMachine.tickTrees()

    # python3.10 -m Behaviour_tree.main
    def initialize(self):
        timenow = time.time()
        wordState = World_State.World_State.get_object()

        while time.time() - timenow < 1:
            self.bobManager.update()
            wordState.update()


def main():
    wordState = World_State.World_State.get_object()
    update_delay = 0.005
    tUpdate = time.time()
    state = StateMockObj()
    state.initialize()

    wordState.update()
    state.update()

    wordState.update()
    state.update(EventClass(EventEnum.ARGENTON_EXPULSO, True))

    wordState.update()
    state.update(EventClass(EventEnum.ARGENTON_EXPULSO, False))

    

    
    #while True:
    #    if time.time() >= update_delay + tUpdate:
    #        wordState.update()
    #        state.update()


if __name__ == "__main__":
    main()
