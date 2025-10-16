from typing import List

from Behaviour_tree.trees.stop import get_stop_tree

from .PlayBase import PlayBase, py_trees


class StopPlay(PlayBase):
    def __init__(self, *args, **kwargs) -> None:
        super.__init__(*args, **kwargs)

    def populate(self):
        halt = get_stop_tree(StopPlay.Kamiji)
        galt2 = get_stop_tree(StopPlay.Argenton)
        galt3 = get_stop_tree(StopPlay.SabKawa)
        self.trees.append(halt)
        self.trees.append(galt3)
        self.trees.append(galt2)
        for tree in self.trees:
            tree.setup()
