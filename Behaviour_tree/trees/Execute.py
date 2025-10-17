# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.plays import (
    AtackPlay,
    CobrarFalta,
    DefensePlay,
    Halt,
    PenaltyDefensePlay,
    PenaltyTeamPlay,
    PreDefense,
    Stop,
)
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

from ..helpers.field_helper import FieldHelper
from .defender.defender_tree import get_defender_tree
from .goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from .ofensive_sup.offensive_suport_tree import get_off_sup_tree
from .suporte_recuado.suporte_recuado import get_pivo_tree

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


def create_scenario(stop: Stop.StopPlay):
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    # --- INICIALIZAR LEITURAS DA WORLD STATE --- #
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        stop.update()
    logger.info("Inicio")
    print("-" * 100)
    return


# EXECUTAR - # python3.10 -m Behaviour_tree.trees.Execute

if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()

    update_delay = 0.001
    tPrint = time.time()
    tUpdate = time.time()

    atackplay = AtackPlay.AtackPlay()
    cobrarfalta = CobrarFalta.CobrarFalta()
    defenseplay = DefensePlay.DefensePlay()
    halt = Halt.HaltPlay()
    penaltydefenseplay = PenaltyDefensePlay.PenaltiDefensePlay()
    penaltyteamplay = PenaltyTeamPlay.PenaltyTaeamPlay()
    predefense = PreDefense.PreDefensePlay()
    stop = Stop.StopPlay()
    create_scenario(stop)
    atackplay.populate()
    while True:
        if time.time() >= update_delay + tUpdate:
            wd.update()
            tUpdate = time.time()
            # gc_state = (_bb.get("gc_state") or "stop").lower()
            atackplay.update()


# if gc_state == "halt":
#     halt.update()

# elif gc_state == "stop":
#     stop.update()

# elif gc_state in ("ready_kickoff_us"):
#     cobrarfalta.update()

# elif gc_state in ("ready_kickoff_them"):
#     defenseplay.update()

# elif gc_state in ("ready_freekick_us",):
#     cobrarfalta.update()

# elif gc_state in ("ready_freekick_them",):
#     defenseplay.update()
# elif gc_state == "ready_penalty_us":
#     penaltyteamplay.update()
# elif gc_state == "ready_penalty_them":
#     penaltydefenseplay.update()
# elif gc_state in ("ball_placement_us", "ball_placement_them"):
#     pass
# elif gc_state == "running":
# else:
#     # no else eu colocaria no stop so por seguranca
#     pass
