from typing import List

from Behaviour_tree.trees.defender.auxiliary_defender_tree import (
    get_auxiliary_defender_tree,
)
from Behaviour_tree.trees.goalkeeper import goalkeeper_tree
from Behaviour_tree.trees.suporte_recuado.suporte_recuado import get_pivo_tree

from .PlayBase import PlayBase, py_trees


class DefensePlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        pivo = get_pivo_tree(self.Kamiji)
        defense_aux = get_auxiliary_defender_tree(self.Argenton)
        goakeeper = goalkeeper_tree.get_goalkeeper_tree(self.SabKawa)
        self.trees.append(pivo)
        self.trees.append(defense_aux)
        self.trees.append(goakeeper)
        for tree in self.trees:
            tree.setup()
