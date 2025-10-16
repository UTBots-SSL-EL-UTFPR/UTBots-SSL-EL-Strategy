from typing import List

from Behaviour_tree.trees.defender import auxiliary_defender_tree, defender_tree
from Behaviour_tree.trees.goalkeeper import goalkeeper_tree

from .PlayBase import PlayBase, py_trees


class DefensePlay(PlayBase):
    def populate(self):
        defensor = defender_tree.get_defender_tree(DefensePlay.Kamiji)
        defensor_aux = auxiliary_defender_tree.get_auxiliary_defender_tree(
            DefensePlay.Argenton
        )
        goakeeper = goalkeeper_tree.get_goalkeeper_tree(DefensePlay.SabKawa)
        self.trees.append(defensor)
        self.trees.append(defensor_aux)
        self.trees.append(goakeeper)
        for tree in self.trees:
            tree.setup()
