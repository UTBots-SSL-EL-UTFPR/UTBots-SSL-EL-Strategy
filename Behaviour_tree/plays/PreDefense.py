from typing import List

from Behaviour_tree.trees.defender.auxiliary_defender_tree import (
    get_auxiliary_defender_tree,
)
from Behaviour_tree.trees.goalkeeper import goalkeeper_tree
from Behaviour_tree.trees.suporte_recuado.suporte_recuado import get_pivo_tree

from .PlayBase import PlayBase, py_trees


class PreDefensePlay(PlayBase):
    def populate(self):
        pivo = get_pivo_tree(PreDefensePlay.Kamiji)
        defense_aux = get_auxiliary_defender_tree(PreDefensePlay.Argenton)
        goakeeper = goalkeeper_tree.get_goalkeeper_tree(PreDefensePlay.SabKawa)
        self.trees.append(pivo)
        self.trees.append(defense_aux)
        self.trees.append(goakeeper)
        for tree in self.trees:
            tree.setup()
