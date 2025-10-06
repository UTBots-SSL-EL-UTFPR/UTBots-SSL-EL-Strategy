import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

# Importa a NOVA função que cria a árvore, em vez da classe antiga
from .defender_tree import get_defender_tree

logging.basicConfig(
    level=logging.INFO, # Mudei para INFO para um log menos poluído durante a execução normal
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


def create_bobs():
    """Cria e reseta os robôs da equipe."""
    a = Bob(TeamID.Kamiji)
    b = Bob(TeamID.Argenton)
    c = Bob(TeamID.SabKawa)
    a.state.reset()
    b.state.reset()
    c.state.reset()
    return a, b, c


def create_scenario(all_bobs: list[Bob]):
    """
    Prepara o ambiente de simulação.
    Futuramente, esta função será modificada para criar cenários de teste específicos.
    """
    wd = World_State.get_object()
    
    # Aguarda um tempo para que o WorldState seja populado com dados iniciais
    logger.info("Aguardando inicialização do World State...")
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        for bob in all_bobs:
            bob.update()
            
    # --- BLOCO DE CRIAÇÃO DE TESTES --- #
    # Os TODOs agora refletem a nova lógica da árvore de comportamento

    # Teste 1: O defensor deve tentar interceptar a bola se ela for uma ameaça ao gol.
    # TODO: Simular a bola se movendo rapidamente em direção ao nosso gol.

    # Teste 2: O defensor deve se posicionar para bloquear uma ameaça.
    # TODO: Simular um oponente com a bola em nossa zona de defesa.

    # Teste 3: O defensor deve retornar à sua posição base se não houver ameaças.
    # TODO: Simular um cenário de jogo neutro, com a bola no meio de campo.

    logger.info("Cenário inicializado. Iniciando simulação da árvore de comportamento.")
    print("-" * 100)
    return


def prints_e_logs(robot: Bob):
    """Exibe informações úteis sobre o estado do robô no console."""
    # Nota: _bb deve ser obtido dentro da função ou passado como argumento
    # para evitar problemas de escopo se este arquivo for importado.
    _bb = Blackboard_Manager.get_instance()
    
    print("=" * 50)
    logger.info(f"ROBÔ: {robot.robot_id.name} ({robot.robot_id.value})")
    logger.info(f"POSIÇÃO ATUAL: {robot.state.position}")
    logger.info(f"ALVO ATUAL: {robot.state.target_position}")
    logger.info(f"COMANDO ATUAL: '{robot.state.current_command}'")

    team_has_ball = _bb.get(BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL)
    logger.info(f"NOSSO TIME TEM A BOLA? -- {team_has_ball}")
    print("=" * 50)


# EXECUTAR - # python3.10 -m Behaviour_tree.trees.defender.test_defender
if __name__ == "__main__":
    # --- Inicialização dos Gerenciadores ---
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    foes = FoesManager()
    
    # --- Criação dos Robôs ---
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]
    
    # --- Configuração do Defensor e sua Árvore de Comportamento ---
    # 1. Escolhe qual robô será o defensor neste teste
    defender_robot = argenton
    
    # 2. Cria a árvore de comportamento USANDO A NOVA FUNÇÃO, passando o objeto robô
    logger.info(f"Atribuindo a árvore de comportamento de defensor ao robô {defender_robot.robot_id.name}")
    defender_behaviour_tree = get_defender_tree(defender_robot)

    # --- Preparação e Execução do Loop de Simulação ---
    create_scenario(all_bobs)
    update_delay = 0.01  # Aumentei um pouco para não sobrecarregar a CPU
    print_delay = 1.0   # Imprimir logs a cada 1 segundo
    
    tPrint = time.time()
    tUpdate = time.time()
    
    while True:
        current_time = time.time()
        
        # Bloco de atualização (lógica principal)
        if current_time >= update_delay + tUpdate:
            wd.update()
            foes.update()
            
            # Executa um "tick" da árvore, fazendo o defensor tomar uma decisão
            defender_behaviour_tree.tick()

            # Atualiza o estado de todos os robôs da equipe
            for bob in all_bobs:
                bob.update()
            tUpdate = current_time
            
        # Bloco para imprimir logs periodicamente
        if current_time >= print_delay + tPrint:
            prints_e_logs(defender_robot)
            tPrint = current_time