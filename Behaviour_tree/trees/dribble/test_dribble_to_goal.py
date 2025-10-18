# Teste: dribble_to_goal_tree
import logging
import time

import py_trees as pt

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from .dribble_to_goal_tree import get_follow_and_dribble_tree

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# EXECUTAR: python -m Behaviour_tree.trees.dribble.test_dribble_to_goal

def _make_bobs():
    a = Bob(TeamID.Kamiji)
    b = Bob(TeamID.Argenton)
    c = Bob(TeamID.SabKawa)
    for rb in (a, b, c):
        rb.state.reset()
    return a, b, c


def _warmup_world_state(seconds: float = 1.0):
    ws = World_State.get_object()
    t0 = time.time()
    while time.time() - t0 < seconds:
        ws.update()
        time.sleep(0.02)


def main():
    ws = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()

    defender,kamiji,  goalkeeper = _make_bobs()
    tree = get_follow_and_dribble_tree(kamiji)

    _warmup_world_state(1.0)

    update_dt = 0.02
    print_dt = 0.2
    t_next_update = time.time()
    t_next_print = time.time()

    while True:
        now = time.time()
        if now >= t_next_update:
            ws.update()
            kamiji.state.update()
            defender.state.update()
            goalkeeper.state.update()
            tree.tick()
            t_next_update = now + update_dt

        if now >= t_next_print:
            pos = kamiji.state.position
            tgt = kamiji.state.target_position
            logger.info(f"KAM position={pos} target={tgt}")
            t_next_print = now + print_dt


if __name__ == "__main__":
    main()
