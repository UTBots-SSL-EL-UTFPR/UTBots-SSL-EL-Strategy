# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

import py_trees

from Behaviour_tree.commom_behaviours.sub_trees.kick_subtree import (
    get_kick_subtree,
    getKickPose,
)
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from Behaviour_tree.robot.bob import Bob, TeamID
from Behaviour_tree.robot.BobManager import BobManager
from Behaviour_tree.robot.FoeState import FoeState
from Behaviour_tree.trees.ofensive_sup.offensive_suport_tree import get_off_sup_tree
from utils.pose2D import Pose2D

from .positioning_helper import PositioningHelper

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


# EXECUTAR - # python3.10 -m Behaviour_tree.helpers.tester
if __name__ == "__main__":
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    hpos = PositioningHelper.get_object()
    bobManager: BobManager = BobManager.get_instance()
    robo1 = bobManager.bobs[TeamID.Argenton]
    _bb.set("super_bob", robo1)
    kicker_tree = get_off_sup_tree("super_bob")
    kicker_tree.setup()
    update_delay = 0.005
    print_delay = 0.5
    tPrint = time.time()
    tUpdate = time.time()
    while True:
        if time.time() >= update_delay + tUpdate:
            wd.update()
            kicker_tree.tick()
            bobManager.update()
            tUpdate = time.time()
