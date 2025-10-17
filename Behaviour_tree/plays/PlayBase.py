from abc import ABC, abstractmethod
from typing import List

import py_trees

from Behaviour_tree.robot.bob import Bob, TeamID
from Behaviour_tree.robot.FoesManager import FoesManager


class PlayBase(ABC):

    Kamiji = Bob(TeamID.Kamiji)
    Argenton = Bob(TeamID.Argenton)
    SabKawa = Bob(TeamID.SabKawa)
    foesManager = FoesManager()

    def __init__(self) -> None:
        self.trees: List[py_trees.trees.BehaviourTree] = []

    @abstractmethod
    def populate():
        pass

    def update(self):
        PlayBase.update_robots()
        for tree in self.trees:
            tree.tick()

    @classmethod
    def update_robots(cls):
        cls.Kamiji.update()
        cls.Argenton.update()
        cls.SabKawa.update()
        cls.foesManager.update()

    def reset(self):
        self.Kamiji.state.reset()
        self.Argenton.state.reset()
        self.SabKawa.state.reset()
