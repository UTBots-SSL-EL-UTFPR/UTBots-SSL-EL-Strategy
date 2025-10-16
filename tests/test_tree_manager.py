import logging
import time
import os
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D
from Behaviour_tree.managers.trees_manager import TreesManager

if __name__ == "__main__":
    trees_manager = TreesManager()
    trees_manager.create()

    ws = World_State.get_object()
    bb = Blackboard_Manager.get_instance()

    while True:
        ws.update()
        trees_manager.update()
        gc_state = (bb.get("gc_state") or "stop").lower()
        print(gc_state)
        #bb.dump()
