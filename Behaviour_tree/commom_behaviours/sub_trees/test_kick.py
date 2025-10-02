import logging
import time
import py_trees as pt
import py_trees.display
from utils.pose2D import Pose2D
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys

from .kick_subtree import KickTree

if __name__ == "__main__":
    # Inicializações
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)-8s | %(message)s")
    logger = logging.getLogger(__name__)

    _bm = BobManager.get_object()
    _ws = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()

    TICK_INTERVAL = 0.1

    try:
        attacker = _bm.get_bob(RobotID.Kamiji)
        if attacker is None:
            raise ValueError("Robôs de passe ou recebimento não encontrados")
    except Exception as e:
        logger.error(f"Erro ao obter robôs: {e}")
        exit(1)

    # Cria a sub árvore de chute
    logger.info(f"Criando árvore de chute para o robô ID: {attacker.robot_id}")
    kick_tree_builder = KickTree(robot_id = attacker.robot_id)
    kick_root_node = kick_tree_builder.create_tree()
    
    attacker_tree = pt.trees.BehaviourTree(kick_root_node)
    attacker_tree.setup(timeout=1.0)

    # Condições iniciais do teste
    logger.info("Configurando condições iniciais no Blackboard...")
    _bb.set(BlackboardKeys.Values.Positions.BALL_POSITION, Pose2D(x=-1000, y=500))
   

    attacker_id_name = attacker.robot_id.name
    has_ball_key = f"{attacker_id_name}{BlackboardKeys.Flags.BallMotion.HAS_BALL}"
    _bb.set(has_ball_key, True)

    logger.info("Início do teste de CHUTE no grSim")

    # Loop principal da simulação
    try:
        while True:
            start_time = time.time()

            _ws.update()
            _bm.update_all()

            # Executa um tick da árvore de comportamento do CHUTE NO GOL
            attacker_tree.tick()

            #print(py_trees.display.unicode_snapshot(root=attacker_tree.root))
            # Aguarda o próximo tick
            elapsed_time = time.time() - start_time
            if elapsed_time < TICK_INTERVAL:
                time.sleep(TICK_INTERVAL - elapsed_time)

    except KeyboardInterrupt:
        logger.info("Teste de CHUTE encerrado pelo usuário.")
    
    