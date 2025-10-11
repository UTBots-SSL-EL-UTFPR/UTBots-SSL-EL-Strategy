# Behaviour_tree/trees/defender/test_defender.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager

# Importa os componentes necessários para a nova lógica
from Behaviour_tree.core.game_state_analyzer import GameStateAnalyzer 
from .defender_tree import get_defender_tree

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def create_bobs():
    """Cria e reseta os robôs da equipe."""
    kamiji = Bob(TeamID.Kamiji)
    argenton = Bob(TeamID.Argenton)
    sabkawa = Bob(TeamID.SabKawa)
    kamiji.state.reset(), argenton.state.reset(), sabkawa.state.reset()
    return kamiji, argenton, sabkawa

def create_scenario(all_bobs: list[Bob]):
    """Prepara o ambiente, aguardando que o WorldState receba dados."""
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

def prints_e_logs(robot_to_watch: Bob):
    """Exibe informações úteis sobre o estado do robô no console."""
    print("=" * 50)
    logger.info(f"ROBÔ DEFENSOR: {robot_to_watch.robot_id.name}")
    logger.info(f"POSIÇÃO ATUAL: {robot_to_watch.state.position}")
    logger.info(f"ALVO ATUAL: {robot_to_watch.state.target_position}")
    logger.info(f"COMANDO ATUAL: '{robot_to_watch.state.current_command}'")
    print("=" * 50)

if __name__ == "__main__":
    # --- Inicialização dos Gerenciadores ---
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

    # --- Preparação do Cenário de Simulação ---
    create_scenario(all_bobs)
    
    # --- Loop de Simulação ---
    update_delay = 0.02  # Frequência alta (50Hz) para movimento fluido
    print_delay = 1.0
    
    tPrint = time.time()
    tUpdate = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            if current_time >= update_delay + tUpdate:
                # 1. PERCEPÇÃO: Ler dados do simulador
                world_state.update()
                foes_manager.update()
                
                # 2. ANÁLISE: Interpretar dados e definir flags
                game_analyzer.update()
                
                # 3. DECISÃO E AÇÃO: A árvore "pensa" e as ações comandam o robô
                defender_tree.tick()
                
                # Atualiza o estado interno dos robôs (como a posição)
                for bob in all_bobs:
                    bob.update()
                
                tUpdate = current_time
                
            if current_time >= print_delay + tPrint:
                prints_e_logs(defender_robot)
                tPrint = current_time

    except KeyboardInterrupt:
        logger.info("Simulação encerrada pelo usuário.")