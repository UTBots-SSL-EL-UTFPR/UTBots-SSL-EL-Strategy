from typing import List

from Behaviour_tree.trees.expulso import get_expulso_tree
from Behaviour_tree.trees.penalty_defense import get_penalty_defense_tree

from .PlayBase import PlayBase, py_trees


class PenaltiDefensePlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        fora1 = get_expulso_tree(PenaltiDefensePlay.Kamiji)
        fora2 = get_expulso_tree(PenaltiDefensePlay.Argenton)
        goleiro = get_penalty_defense_tree(PenaltiDefensePlay.SabKawa)
        self.trees.append(fora1)
        self.trees.append(fora2)
        self.trees.append(goleiro)
        for tree in self.trees:
            tree.setup()
