# trees/strategy_tree.py
#estrategia macro time

from trees.tree import Tree
from py_trees.behaviours import Running

class StrategyTree(Tree):
    def __init__(self):
        super().__init__(name="StrategyTree")

    def create_tree(self):
        return Running(name="Estratégia global")
