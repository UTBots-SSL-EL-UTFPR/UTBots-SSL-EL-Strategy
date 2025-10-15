from abc import ABC, abstractmethod
from typing import List

import py_trees

from Behaviour_tree.robot.bob import Bob, TeamID
from Behaviour_tree.robot.FoesManager import FoesManager


class PlayBase(ABC):

    def __init__(self) -> None:
        self.trees: List[py_trees.trees.BehaviourTree]
        self.Kamiji = Bob(TeamID.Kamiji)
        self.Argenton = Bob(TeamID.Argenton)
        self.SabKawa = Bob(TeamID.SabKawa)
        self.foesManager = FoesManager()

    @abstractmethod
    def populate():
        pass

    def update(self):
        for tree in self.trees:
            tree.tick()

    def reset(self):
        self.Kamiji.state.reset()
        self.Argenton.state.reset()
        self.SabKawa.state.reset()
