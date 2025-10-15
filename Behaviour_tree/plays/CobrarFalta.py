from typing import List

from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.trees.goalkeeper import goalkeeper_tree
from Behaviour_tree.trees.ofensive_sup.offensive_suport_tree import get_off_sup_tree
from Behaviour_tree.trees.suporte_recuado.suporte_recuado import get_pivo_tree

from .PlayBase import PlayBase, py_trees


class DefensePlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        wd = World_State.get_object()
        ball_X = wd.get_ball_position().x
        if ball_X * FieldHelper.get_team_goal_center().x > 0:
            off_sup = get_off_sup_tree(self.Kamiji)
            pivo = get_pivo_tree(self.Argenton)
            # cobrador = get_cobrador_tree(self.SabKawa)
            self.trees.append(pivo)

        else:
            # cobrador = get_cobrador_tree(self.Argenton)
            off_sup = get_off_sup_tree(self.Kamiji)
            goakeeper = goalkeeper_tree.get_goalkeeper_tree(self.SabKawa)
            self.trees.append(goakeeper)

        self.trees.append(off_sup)
        # self.trees.append(cobrador)
        for tree in self.trees:
            tree.setup()
