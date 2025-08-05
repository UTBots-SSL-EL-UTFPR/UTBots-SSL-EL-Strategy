# trees/bob_trees/defender_tree.py

from trees.tree import Tree
from py_trees.behaviours import Success

class Defender_tree(Tree):
    def __init__(self, bob):
        self.bob = bob
        super().__init__(name="defender_tree")

    def create_tree(self):
        return Success(name="Comportamento inicial do defensor")
