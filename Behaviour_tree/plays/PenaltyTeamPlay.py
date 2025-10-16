from typing import List

from Behaviour_tree.trees.expulso import get_expulso_tree
from Behaviour_tree.trees.penalty import get_penalty_tree

from .PlayBase import PlayBase, py_trees


class PenaltyTaeamPlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        fora1 = get_expulso_tree(PenaltyTaeamPlay.Kamiji)
        batedor = get_penalty_tree(PenaltyTaeamPlay.Argenton)
        fora2 = get_expulso_tree(PenaltyTaeamPlay.SabKawa)
        self.trees.append(fora1)
        self.trees.append(fora2)
        self.trees.append(batedor)
        for tree in self.trees:
            tree.setup()
