# trees/bob_trees/kamiji_tree.py

from trees.tree import Tree
from py_trees.behaviours import Success

class KamijiTree(Tree):
    def __init__(self, bob):
        self.bob = bob
        super().__init__(name="KamijiTree")

    def create_tree(self):
        return Success(name="Comportamento inicial do Kamiji")
