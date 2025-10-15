from typing import List

from Behaviour_tree.trees.halt import get_halt_tree

from .PlayBase import PlayBase, py_trees


class DefensePlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        halt = get_halt_tree(self.Kamiji)
        galt2 = get_halt_tree(self.Argenton)
        galt3 = get_halt_tree(self.SabKawa)
        self.trees.append(halt)
        self.trees.append(galt3)
        self.trees.append(galt2)
        for tree in self.trees:
            tree.setup()
