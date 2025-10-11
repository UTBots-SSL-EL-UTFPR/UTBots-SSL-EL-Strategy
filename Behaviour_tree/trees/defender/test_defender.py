# Behaviour_tree/trees/defender/test_defender.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

# Importa o analisador de estado do jogo
from Behaviour_tree.core.game_state_analyzer import GameStateAnalyzer 

# Importa apenas a árvore que vamos testar
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
    Prepara o ambiente, aguardando que o WorldState receba dados.
    """
    wd = World_State.get_object()
    
    logger.info("Aguardando inicialização do World State (2 segundos)...")
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        for bob in all_bobs:
            bob.update()
            
    logger.info("World State inicializado. Iniciando simulação do defensor.")
    print("-" * 100)
    return


def prints_e_logs(robot_to_watch: Bob):
    """Exibe informações úteis sobre o estado do robô no console."""
    print("=" * 50)
    logger.info(f"ROBÔ DEFENSOR: {robot_to_watch.robot_id.name}")
    logger.info(f"POSIÇÃO ATUAL: {robot_to_watch.state.position}")
    logger.info(f"ALVO ATUAL: {robot_to_watch.state.target_position}")
    logger.info(f"COMANDO ATUAL: '{robot_to_watch.state.current_command}'")
    print("=" * 50)


# ==============================================================================#
# BLOCO PRINCIPAL DE EXECUÇÃO                                                   #
# ==============================================================================#

if __name__ == "__main__":
    # --- Inicialização dos Gerenciadores ---
    bob_manager = BobManager.get_object()
    world_state = World_State.get_object()
    foes_manager = FoesManager()
    game_analyzer = GameStateAnalyzer()
    
    # --- Criação dos Robôs ---
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]
    
    # --- Atribuição de Papel (Apenas para o Defensor) ---
    defender_robot = argenton
    logger.info(f"Atribuindo árvore de comportamento de defensor ao robô {defender_robot.robot_id.name}")
    defender_tree = get_defender_tree(defender_robot)

    # As árvores dos outros robôs não são criadas neste teste focado.

    # --- Preparação do Cenário de Simulação ---
    create_scenario(all_bobs)
    
    # --- Loop de Simulação ---
    update_delay = 0.001
    print_delay = 0.5
    
    tPrint = time.time()
    tUpdate = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            # Bloco de atualização (lógica principal)
            if current_time >= update_delay + tUpdate:
                # 1. Percepção
                world_state.update()
                foes_manager.update()
                
                # 2. Análise
                game_analyzer.update()
                
                # 3. Decisão (Apenas o defensor "pensa")
                defender_tree.tick()
                
                # 4. Ação (Todos os robôs são atualizados para refletir o estado)
                for bob in all_bobs:
                    bob.update()
                
                tUpdate = current_time
                
            # Bloco para imprimir logs periodicamente
            if current_time >= print_delay + tPrint:
                prints_e_logs(defender_robot)
                tPrint = current_time

    except KeyboardInterrupt:
        logger.info("Simulação encerrada pelo usuário.")