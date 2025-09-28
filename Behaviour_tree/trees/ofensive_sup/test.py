# teste movimentação
import time

import py_trees as pt

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.positioning.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from ....behaviors.common import actions as action_nodes
from ....behaviors.common import condition as condition_nodes
from ...tree import Tree

navigation_flags = BlackboardKeys.Flags.motion.navigation
positions = BlackboardKeys.Values.Positions

TICK_INTERVAL = 0.1
UPDATE_INTERVAL = TICK_INTERVAL / 2


def main() -> None:
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    kamiji = bob_state.get_bob(RobotID.Kamiji)
    defensor = bob_state.get_bob(RobotID.Defender)
    goalkeeper = bob_state.get_bob(RobotID.Goalkeeper)
    ph = PositioningHelper.get_object()

    if kamiji is None or defensor is None or goalkeeper is None:
        return

    # kamiji_tree
    move = action_nodes.Move_node("move kamiji", kamiji, 15)
    sequence = pt.composites.Sequence("sequencia", True, [move])
    kamiji_tree = pt.trees.BehaviourTree(sequence)

    print("\n--- SETUP ---")
    kamiji_tree_setup_args = {"bob": kamiji, "planner": 11}
    kamiji_tree.setup(timeout=1.0, visitor=None, **kamiji_tree_setup_args)

    # defensor_tree
    move = action_nodes.Move_node("move defensor", defensor, 15)
    sequence = pt.composites.Sequence("sequencia", True, [move])
    defensor_tree = pt.trees.BehaviourTree(sequence)
    defensor_tree_setup_args = {"bob": defensor, "planner": 11}
    defensor_tree.setup(timeout=1.0, visitor=None, **defensor_tree_setup_args)

    move = action_nodes.Move_node("move goalkeeper", goalkeeper, 15)
    sequence = pt.composites.Sequence("sequencia", True, [move])
    goalkeeper_tree = pt.trees.BehaviourTree(sequence)
    defensor_tree_setup_args = {"bob": defensor, "planner": 11}
    goalkeeper_tree.setup(timeout=1.0, visitor=None, **defensor_tree_setup_args)

    # -----------------------------------------------------------#
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()

    print("\n--- LOOP ---")

    wd.update()
    bob_state.update_all()
    bob_state.set_bob_freekick_position()
    print("-" * 100)

    delay = 0.1
    t0 = time.time()

    while True:
        if time.time() >= delay + t0:
            wd.update()

            bob_state.update_all()
            kamiji_tree.tick()
            defensor_tree.tick()
            goalkeeper_tree.tick()
            print(
                _bb.get(
                    f"{defensor.robot_id.name}{BlackboardKeys.Values.Positions.pos_ball_visible}"
                )
            )

            t0 = time.time()


if __name__ == "__main__":
    main()
