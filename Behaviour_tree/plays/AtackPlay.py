from typing import List

from Behaviour_tree.trees.goalkeeper import goalkeeper_tree
from Behaviour_tree.trees.ofensive_sup.offensive_suport_tree import get_off_sup_tree
from Behaviour_tree.trees.suporte_recuado.suporte_recuado import get_pivo_tree

from .PlayBase import PlayBase, py_trees


class AtackPlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        pivo = get_pivo_tree(AtackPlay.Kamiji)
        off_sup = get_off_sup_tree(AtackPlay.Argenton)
        goakeeper = goalkeeper_tree.get_goalkeeper_tree(AtackPlay.SabKawa)
        self.trees.append(pivo)
        self.trees.append(off_sup)
        self.trees.append(goakeeper)
        for tree in self.trees:
            tree.setup()
