import time
from core.event_callbacks import subscribe_all
from robot.bob import Bob
import py_trees

# Supondo que você tenha definido os papéis assim:
from core.Field import RobotID

def main():
    # 1. Inicializa o sistema de eventos
    subscribe_all()

    # 2. Cria robô e árvore
    bob = Bob(robot_id=RobotID.Kamiji)
    bt_root = create_attacker_tree(bob)
    behavior_tree = py_trees.trees.BehaviourTree(bt_root)
    behavior_tree.setup(timeout=15)

    # 3. Loop principal
    while True:
        # (1) Atualiza percepção (Field → BobState)
        bob.state.update()

        # (2) O BobState dispara eventos (se necessário)
        # → Já integrado no update()

        # (3) Árvores tomam decisão com base no Blackboard
        behavior_tree.tick()

        # (4) Espera até o próximo ciclo (ex: 20 Hz → 0.05s)
        time.sleep(0.05)

if __name__ == "__main__":
    main()
