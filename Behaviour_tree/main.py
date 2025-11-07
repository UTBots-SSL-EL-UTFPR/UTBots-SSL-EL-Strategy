import logging
import time
from typing import List

import py_trees

from .core import World_State
from .robot.BobManager import Bob, BobManager, TeamID
from .trees.defender.defender_tree import get_defender_tree
from .trees.goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from .trees.pivo.pivo import get_pivo_tree

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class StateMockObj:
    def __init__(self) -> None:
        self.bobManager: BobManager = BobManager.get_instance()
        self.trees: List[py_trees.trees.BehaviourTree] = []
        self.setup_trees()

    def setup_trees(self):
        a = 1
        bobs = self.bobManager.bobs
        goalkeeper = get_goalkeeper_tree(bobs[TeamID.SabKawa])
        if a:
            defensor = get_defender_tree(bobs[TeamID.Kamiji])
            pivo = get_pivo_tree(bobs[TeamID.Argenton])
            #self.trees.append(defensor)
            self.trees.append(pivo)
        self.trees.append(goalkeeper)

    def tick_trees(self):
        for tree in self.trees:
            tree.tick()
            return

    def update(self):
        self.bobManager.update()
        self.tick_trees()

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
    while True:
        if time.time() >= update_delay + tUpdate:
            wordState.update()
            state.update()


if __name__ == "__main__":
    main()
