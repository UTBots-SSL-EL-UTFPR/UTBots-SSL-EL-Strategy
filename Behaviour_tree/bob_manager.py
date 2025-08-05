# core/bob_manager.py

from Behaviour_tree.trees.tree import Tree
from robot.bob import Bob
from trees.bob_trees.kamiji_tree import KamijiTree
from trees.bob_trees.defender_tree import Defender_tree
from trees.bob_trees.goalkeeper_tree import Goalkeeper_tree
from core.Field import RobotID
from typing import Dict

class BobManager:
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.bobs: Dict[RobotID, Bob] = {}
        self.trees: Dict[RobotID, Tree] = {}

        self._create_bob(RobotID.Kamiji, KamijiTree)
        self._create_bob(RobotID.Defender, Defender_tree)
        self._create_bob(RobotID.Goalkeeper, Goalkeeper_tree)

    def _create_bob(self, robot_id, tree):
        """
        Cria uma instância de Bob e associa à sua árvore.

        Args:
            robot_id (RobotID): ID do robô.
            tree (Tree): Classe da árvore associada.
        """
        bob = Bob(robot_id=robot_id)
        self.bobs[robot_id] = bob
        self.trees[robot_id] = tree(bob)

    def update_all(self):
        for bob in self.bobs.values():
            bob.state.update()

    def tick_all(self):
        for tree in self.trees.values():
            tree.tick()

    def get_bob(self, robot_id):
        return self.bobs.get(robot_id)

    def get_tree(self, robot_id):
        return self.trees.get(robot_id)
