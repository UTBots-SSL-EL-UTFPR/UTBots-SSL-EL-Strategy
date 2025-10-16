from typing import List

from Behaviour_tree.trees.halt import get_halt_tree

from .PlayBase import PlayBase, py_trees


class HaltPlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        halt = get_halt_tree(HaltPlay.Kamiji)
        galt2 = get_halt_tree(HaltPlay.Argenton)
        galt3 = get_halt_tree(HaltPlay.SabKawa)
        self.trees.append(halt)
        self.trees.append(galt3)
        self.trees.append(galt2)
        for tree in self.trees:
            tree.setup()
