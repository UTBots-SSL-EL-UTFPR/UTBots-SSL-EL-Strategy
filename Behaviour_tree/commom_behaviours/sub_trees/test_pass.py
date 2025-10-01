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


from .pass_subtree import PassTree

# ==============================================================================#
# BLOCO DE TESTE PRINCIPAL (para rodar no grSim)                               #
# ==============================================================================#

if __name__ == "__main__":
    # --- 1. INICIALIZAÇÃO GERAL ---
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(levelname)-8s | %(message)s")
    logger = logging.getLogger(__name__)

    bob_manager = BobManager.get_object()
    world_state = World_State.get_object()
    blackboard = Blackboard_Manager.get_instance()
    
    TICK_INTERVAL = 0.1

    # --- 2. PEGAR OS ROBÔS NECESSÁRIOS PARA O PASSE ---
    try:
        passer = bob_manager.get_bob(RobotID.Kamiji)
        receiver = bob_manager.get_bob(RobotID.Defender)
        if passer is None or receiver is None:
            raise ValueError("Robôs de passe ou recebimento não encontrados")
    except Exception as e:
        logger.error(f"Erro ao obter robôs: {e}")
        exit(1)

    # --- 3. CRIAR A ÁRVORE DE COMPORTAMENTO (AGORA DE FORMA SIMPLES) ---
    logger.info(f"Criando árvore de passe para o robô ID: {passer.robot_id}")
    pass_tree_builder = PassTree(robot_id=passer.robot_id)
    pass_root_node = pass_tree_builder.create_tree()
    
    passer_tree = pt.trees.BehaviourTree(pass_root_node)
    passer_tree.setup(timeout=1.0)

    # --- 4. CONFIGURAR O ESTADO INICIAL DO MUNDO (CONDIÇÕES DO TESTE) ---
    logger.info("Configurando condições iniciais no Blackboard...")
    blackboard.set(BlackboardKeys.Values.Positions.BALL_POSITION, Pose2D(x=-1000, y=500))
   

    passer_id_name = passer.robot_id.name
    has_ball_key = f"{passer_id_name}{BlackboardKeys.Flags.BallMotion.HAS_BALL}"
    blackboard.set(has_ball_key, True)

    
    logger.info("Início do teste de PASSE no grSim")

    # --- 5. LOOP DE SIMULAÇÃO ---
    try:
        while True:
            start_time = time.time()

            world_state.update()
            bob_manager.update_all()

            # Executa um tick da árvore de comportamento do PASSE
            passer_tree.tick()

            #print(py_trees.display.unicode_snapshot(root=passer_tree.root))
            # Aguarda o próximo tick
            elapsed_time = time.time() - start_time
            if elapsed_time < TICK_INTERVAL:
                time.sleep(TICK_INTERVAL - elapsed_time)

    except KeyboardInterrupt:
        logger.info("Teste de PASSE encerrado pelo usuário.")
 
