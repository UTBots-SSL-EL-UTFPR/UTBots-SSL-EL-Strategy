# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

from ..goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from .offensive_suport_tree import get_off_sup_tree

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

    logger.info("Inicio simulacao")
    print("-" * 100)
    return


def prints_e_logs(robot: Bob, others: list[Bob]):
    pass


# EXECUTAR - # python3.10 -m Behaviour_tree.trees.ofensive_sup.teste
if __name__ == "__main__":
    wd = World_State.get_object()
    bb = Blackboard_Manager.get_instance()
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]

    create_scenario(all_bobs)
    update_delay = 0.02
    print_delay = 0.5
    tPrint = time.time()
    tUpdate = time.time()
    argenton.set_new_target_position(Pose2D(0, 0, -2))
    var = 0
    while True:
        if time.time() >= print_delay + tPrint:
            prints_e_logs(argenton, [kamiji, goalkeeper])
            tPrint = time.time()
        if time.time() >= update_delay + tUpdate:
            argenton.update()
            wd.update()

            argenton.precision_movement()
            tUpdate = time.time()
