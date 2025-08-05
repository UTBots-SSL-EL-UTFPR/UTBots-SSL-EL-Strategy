# trees/bob_trees/Goalkeeper_tree.py

from trees.tree import Tree
from py_trees.behaviours import Success

class Goalkeeper_tree(Tree):
    def __init__(self, bob):
        self.bob = bob
        super().__init__(name="Goalkeeper_tree")

    def create_tree(self):
        return Success(name="Comportamento inicial do goleiro")
