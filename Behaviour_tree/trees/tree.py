# trees/tree.py

import abc
import py_trees
from ..core.blackboard import Blackboard_Manager

class Tree(abc.ABC):
    """
    Classe abstrata.

    Subclasses devem implementar o método `create_tree`.

    Atributos:
        name -> recurso grafico
        root 
        tree (py_trees.trees.BehaviourTree): Instância da árvore executável.
    """

    def __init__(self, name: str):

        self.name = name
        self.root = self.create_tree()
        self._bb = Blackboard_Manager.get_instance()
        self.tree = py_trees.trees.BehaviourTree(self.root)
        self.tree.setup(timeout=5)

    @abc.abstractmethod
    def create_tree(self) -> py_trees.behaviour.Behaviour:
        """
        Returns:
            py_trees.behaviour.Behaviour: raiz da arvore.
        """
        pass

    def tick(self):
        self.tree.tick()

    def get_flag(self, key: str):
        """
        Recupera uma flag do Blackboard.
        """
        return self._bb.get(key)