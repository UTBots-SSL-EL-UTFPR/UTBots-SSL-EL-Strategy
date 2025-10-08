import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

from .defender_tree import get_defender_tree

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ==============================================================================#
# FUNÇÕES AUXILIARES DE TESTE                                                   #
# ==============================================================================#

def create_bobs():
    """Cria e reseta os robôs da equipe."""
    kamiji = Bob(TeamID.Kamiji)
    argenton = Bob(TeamID.Argenton)
    sabkawa = Bob(TeamID.SabKawa)
    
    kamiji.state.reset()
    argenton.state.reset()
    sabkawa.state.reset()
    
    return kamiji, argenton, sabkawa


def create_scenario(all_bobs: list[Bob]):
    """
    Prepara o ambiente de simulação, aguardando que o WorldState receba
    os primeiros dados da visão/simulador.
    """
    wd = World_State.get_object()
    
    logger.info("Aguardando inicialização do World State (2 segundos)...")
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        # Durante a inicialização, o WorldState já começa a popular o Blackboard
        wd.update()
        for bob in all_bobs:
            bob.update()
            
    logger.info("World State inicializado. Iniciando simulação da árvore de comportamento.")
    print("-" * 100)


def prints_e_logs(robot: Bob):
    """Exibe informações úteis sobre o estado do robô no console."""
    print("=" * 50)
    logger.info(f"ROBÔ: {robot.robot_id.name} ({robot.robot_id.value})")
    logger.info(f"POSIÇÃO ATUAL: {robot.state.position}")
    logger.info(f"ALVO ATUAL: {robot.state.target_position}")
    logger.info(f"COMANDO ATUAL: '{robot.state.current_command}'")
    print("=" * 50)

# ==============================================================================#
# BLOCO PRINCIPAL DE EXECUÇÃO                                                   #
# ==============================================================================#

# EXECUTAR - # python3.10 -m Behaviour_tree.trees.defender.test_defender
if __name__ == "__main__":
    # --- Inicialização dos Gerenciadores ---
    bob_manager = BobManager.get_object()
    world_state = World_State.get_object()
    foes_manager = FoesManager()
    
    # --- Criação dos Robôs ---
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]
    
    # --- Configuração do Defensor e sua Árvore de Comportamento ---
    defender_robot = argenton
    logger.info(f"Atribuindo a árvore de comportamento de defensor ao robô {defender_robot.robot_id.name}")
    defender_behaviour_tree = get_defender_tree(defender_robot)

    # --- Preparação do Cenário de Simulação ---
    create_scenario(all_bobs)
    
    # --- Loop de Simulação ---
    update_delay = 0.1  # Executa a árvore 10 vezes por segundo
    print_delay = 1.0   # Imprime logs a cada 1 segundo
    
    tPrint = time.time()
    tUpdate = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Bloco de atualização (lógica principal)
            if current_time >= update_delay + tUpdate:
                # CORREÇÃO: WorldState e FoesManager são atualizados a cada ciclo
                world_state.update()
                foes_manager.update()
                
                # Executa um "tick" da árvore, fazendo o defensor tomar uma decisão
                defender_behaviour_tree.tick()

                # Atualiza o estado de todos os robôs da equipe (processa os comandos)
                for bob in all_bobs:
                    bob.update()
                tUpdate = current_time
                
            # Bloco para imprimir logs periodicamente
            if current_time >= print_delay + tPrint:
                prints_e_logs(defender_robot)
                tPrint = current_time

    except KeyboardInterrupt:
        logger.info("Teste do defensor encerrado pelo usuário.")