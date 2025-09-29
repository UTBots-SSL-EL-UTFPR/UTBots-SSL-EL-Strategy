# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from .offensive_suport_tree import get_off_sup_tree

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


def create_bobs():
    a = Bob(RobotID.Kamiji)
    b = Bob(RobotID.Defender)
    c = Bob(RobotID.Goalkeeper)
    a.state.reset()
    b.state.reset()
    c.state.reset()
    return a, b, c


def create_scenario(all_bobs: list[Bob]):
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    # --- INICIALIZAR LEITURAS DA WORLD STATE --- #
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        for bob in all_bobs:
            bob.update()
    # --- BLOCO DE CRIACAO DE TESTES --- #

    # teste 1. O robo deve chutar ou passar quando esta com a bola.
    # sub teste 1. O robo deve chutar se gol aberto
    # TODO
    # sub teste 2. O robo deve passar
    # TODO

    # teste 2. o robo deve brigar pela bola se a bola não for nossa
    # sub teste 1. O robo deve pressionar o oponente se ele estiver com a bola
    # sub teste 2. O robo deve buscar e recuperar a bola se ela estiver solta

    # teste 3. o robo deve reposicionar se a bola for aliada
    # sub teste 1. O robo deve se posicionar para rebote em caso de chute
    # sub teste 2. O robo deve se posicionar para receber passe em caso de passe
    # sub teste 3. O robo deve se posicionar como suporte ofencivo em caso de preparacao

    logger.info("Inicio simulacao")
    print("-" * 100)
    return


def prints_e_logs(robot: Bob, others: list[Bob]):

    team_has_ball = _bb.get(BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL)
    logger.info(f"time tem a bola? -- {team_has_ball}")
    print("+++ ----------------------------- +++")

    logger.info(f"ID -- {robot.robot_id.value}")
    logger.info(f"POSITION -- {robot.state.position}")

    logger.info(f"TARGET -- {robot.state.target_position}")
    logger.info(f"-- {robot.state.current_command}")

    print("=" * 50)


# EXECUTAR - # python3.10 -m Behaviour_tree.trees.ofensive_sup.test_off_sup
if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]
    off_sup_subtree = get_off_sup_tree(argenton)

    create_scenario(all_bobs)
    update_delay = 0.02
    print_delay = 0.1
    tPrint = time.time()
    tUpdate = time.time()
    while True:
        if time.time() >= print_delay + tPrint:
            # prints_e_logs(argenton, [kamiji, goalkeeper])
            tPrint = time.time()
        if time.time() >= update_delay + tUpdate:
            wd.update()
            off_sup_subtree.tick()

            for bob in all_bobs:
                bob.update()
            tUpdate = time.time()
