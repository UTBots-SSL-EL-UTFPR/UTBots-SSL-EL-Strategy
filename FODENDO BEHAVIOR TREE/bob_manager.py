"""
Arquivo utilizado como EXECUTORA DA ARVORE
controlará todos os bobs
"""

# ssl_robot_controller/main.py

import py_trees
import py_trees.console as console
import time
from robot.bob import Bob
from bob_trees.attacker_tree import Attacker_tree
#import field

def create_robot_and_tree(role: str, robot_id: str):
    """Cria uma instância de robô e sua árvore de comportamento."""
    #robot = Robot(robot_id)
    # if role == "attacker":
    #     return robot, AttackerTree(f"Attacker Tree ({robot_id})", robot)

def main():
    """Função principal para execução das árvores de comportamento."""

    # Criação de robôs e suas árvores
    attacker_robot, attacker_tree_root = create_robot_and_tree("attacker", "Attacker_01")

    # Configura e executa a árvore do atacante
    # attacker_tree = py_trees.trees.BehaviourTree(attacker_tree_root)
    # attacker_tree.setup(timeout=15) # Tempo limite para setup
    # for i in range(1, 10):
    #     attacker_tree.tick()
    #     time.sleep(0.5)

    # Resetar o estado do field e bob para a próxima iteração
    # world_model.__init__()
    # attacker_robot.__init__("Attacker_01")

   

if __name__ == "__main__":
    main()