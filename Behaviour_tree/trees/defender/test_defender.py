import logging
import time

import py_trees as pt

from Behaviour_tree.managers.bob_manager import BobManager
from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.trees.defender.defender_tree import DefenderTree
from utils.pose2D import Pose2D

TICK_INTERVAL = 0.1
UPDATE_INTERVAL = TICK_INTERVAL / 2

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#

if __name__ == "__main__":
    # Inicializa os objetos principais
    bob_manager = BobManager.get_object()
    world_state = World_State.get_object()
    blackboard = Blackboard_Manager.get_instance()
    positioning_helper = Positioning_helper.get_object()

    # Obtém o robô defensor
    defender = bob_manager.get_bob(RobotID.Defender)
    if defender is None:
        logger.error("Defensor não encontrado!")
        exit(1)

    # Cria a árvore de comportamento do defensor
    defender_tree = DefenderTree(robot_id=RobotID.Defender)
    tree = defender_tree.create_tree()
    behaviour_tree = pt.trees.BehaviourTree(tree)
    behaviour_tree.setup(timeout=1.0)

    # Configurações iniciais do blackboard
    blackboard.set("ball_position", Pose2D(-1500, 0))  # Posição inicial da bola
    blackboard.set("ball_velocity", Pose2D(-100, 0))  # Velocidade inicial da bola
    blackboard.set("opponents_positions", [Pose2D(-1600, 200)])  # Posição dos oponentes

    logger.info("Início do teste do defensor")

    # Loop de simulação
    try:
        while True:
            start_time = time.time()

            # Atualiza o estado do mundo e do robô
            world_state.update()
            bob_manager.update_all()

            # Executa um tick da árvore de comportamento
            behaviour_tree.tick()

            # Aguarda o próximo tick
            elapsed_time = time.time() - start_time
            time.sleep(max(0, TICK_INTERVAL - elapsed_time))

    except KeyboardInterrupt:
        logger.info("Teste do defensor encerrado pelo usuário.")