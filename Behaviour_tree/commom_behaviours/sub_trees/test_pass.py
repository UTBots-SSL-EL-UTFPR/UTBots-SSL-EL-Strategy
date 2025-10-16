# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from .pass_subtree import get_pass_subtree

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


def create_bobs():
    a = Bob(TeamID.Kamiji)
    b = Bob(TeamID.Argenton)
    c = Bob(TeamID.SabKawa)
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


# EXECUTAR: python3 -m Behaviour_tree.commom_behaviours.sub_trees.test_pass
if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    kamiji, argenton, SabKawa = create_bobs()
    all_bobs = [kamiji, argenton, SabKawa]
    pass_subtree = get_pass_subtree(SabKawa)

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
            for b in all_bobs:
                b.state.update()
            pass_subtree.tick()
            tUpdate = time.time()