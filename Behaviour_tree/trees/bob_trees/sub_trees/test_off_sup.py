import logging
import time

import py_trees as pt

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from ....behaviors.common import actions as action_nodes
from ....behaviors.common import condition as condition_nodes
from ...tree import Tree

navigation_flags = BB_flags_and_values.Flags.motion.navigation
positions = BB_flags_and_values.Values.Positions

TICK_INTERVAL = 0.1
UPDATE_INTERVAL = TICK_INTERVAL / 2

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    kamiji = bob_state.get_bob(RobotID.Kamiji)
    defensor = bob_state.get_bob(RobotID.Defender)
    goalkeeper = bob_state.get_bob(RobotID.Goalkeeper)
    ph = Positioning_helper.get_object()
    if kamiji is None or defensor is None or goalkeeper is None:
        exit(1)

    # defensor_tree
    suport_repos = pt.composites.Selector(
        "posicionamento receber passe ou rebote",
        False,
        children=[
            action_nodes.Receive_pass("pass", defensor),
            action_nodes.Rebound_position("rebound", defensor),
        ],
    )
    sequence = pt.composites.Sequence(
        "movimento passe/rebote",
        True,
        children=[suport_repos, action_nodes.Move_node("Move", defensor, 15)],
    )
    defensor_tree = pt.trees.BehaviourTree(sequence)
    defensor_tree_setup_args = {}
    defensor_tree.setup(timeout=1.0, visitor=None, **defensor_tree_setup_args)

    # goalkeeper
    move = action_nodes.Move_node("move goalkeeper", goalkeeper, 15)
    sequence = pt.composites.Sequence("sequencia", True, [move])
    goalkeeper_tree = pt.trees.BehaviourTree(sequence)
    defensor_tree_setup_args = {}
    goalkeeper_tree.setup(timeout=1.0, visitor=None, **defensor_tree_setup_args)

    _bb.set(
        f"{defensor.robot_id.name}{callbacks.BB_flags_and_values.Flags.Team_Flags.kick_actions.team_pass}",
        False,
    )
    _bb.set(
        f"{callbacks.BB_flags_and_values.Flags.Team_Flags.kick_actions.team_kick}",
        True,
    )
    _bb.set(
        f"{callbacks.BB_flags_and_values.Values.Positions.pos_pass_target}",
        Pose2D(1150, -1000),
    )

    # -----------------------------------------------------------#
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        bob_state.update_all()
    logger.info("Inicio jogo")

    bob_state.set_bob_freekick_position()
    print("-" * 100)

    delay = 0.01
    t0 = time.time()

    while True:
        if time.time() >= delay + t0:
            wd.update()

            bob_state.update_all()
            defensor_tree.tick()
            goalkeeper_tree.tick()

            t0 = time.time()
