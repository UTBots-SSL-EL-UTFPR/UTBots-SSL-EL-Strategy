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


def prints_e_logs(robot: Bob, others: list[Bob]):

    team_has_ball = _bb.get(BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL)
    logger.info(f"time tem a bola? -- {team_has_ball}")
    print("+++ ----------------------------- +++")

    logger.info(f"ID -- {robot.robot_id.value}")
    logger.info(f"POSITION -- {robot.state.position}")

    logger.info(f"TARGET -- {robot.state.target_position}")
    logger.info(f"-- {robot.state.current_command}")
    logger.info(
        f"{_bb.get(BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL)} team has ball"
    )

    print("=" * 50)


# EXECUTAR - python3.10 -m Behaviour_tree.trees.suporte_recuado.testeV2
if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()

    atackplay = AtackPlay.AtackPlay()
    cobrarfalta = CobrarFalta.CobrarFalta()
    defenseplay = DefensePlay.DefensePlay()
    halt = Halt.HaltPlay()
    penaltydefenseplay = PenaltyDefensePlay.PenaltiDefensePlay()
    penaltyteamplay = PenaltyTeamPlay.PenaltyTaeamPlay()
    predefense = PreDefense.PreDefensePlay()
    stop = Stop.StopPlay()

    atackplay.populate()
    cobrarfalta.populate()
    defenseplay.populate()
    halt.populate()
    penaltydefenseplay.populate()
    penaltyteamplay.populate()
    predefense.populate()
    stop.populate()

    create_scenario(stop)
    update_delay = 0.001
    tPrint = time.time()
    tUpdate = time.time()
    while True:
        atackplay.update_robots()
        wd.update()

        if time.time() >= update_delay + tUpdate:
            atackplay.update()
            tUpdate = time.time()
