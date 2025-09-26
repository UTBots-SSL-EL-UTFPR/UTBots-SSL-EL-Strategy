"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""

from __future__ import annotations

import logging
import math
import time
from time import sleep

import py_trees

from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys

from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.bob_manager import BobManager

navigation_flags = BlackboardKeys.Flags.motion.navigation
positions = BlackboardKeys.Values.Positions
team_flags = BlackboardKeys.Flags.Team_Flags
import time
from typing import Optional, Tuple

import py_trees as pt

team_flags = BlackboardKeys.Flags.Team_Flags
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.robot.bob import Bob

from ...positioning import positioning_helper as Positioning_helper

from commom_behaviours.actions import MovimentoUnico, RecuperarBola
from commom_behaviours.condition import FoesHaveBall, HasBall
# ---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
# ---------------------------------------------------------------------------------------#
logger = logging.getLogger(__name__)

def get_goalkeeper_tree(robot: Bob) -> pt.behaviour.Behaviour:

    recuperar_bola = RecuperarBola(robot, name="RecuperarBola")
    movimento_unico = MovimentoUnico(robot, name="MovimentoUnico")

    bola_solta = py_trees.composites.Sequence(name="Bola_Solta", memory=False, children=[recuperar_bola, movimento_unico])
    
    foesHasBall = FoesHaveBall()
    goalkeeperCommonPosition = GoalkeeperCommonPosition(robot)

    defesa_comum = py_trees.composites.Sequence(name="Defesa_Comum", memory=False, children=[foesHasBall, goalkeeperCommonPosition])

    root = py_trees.composites.Selector(name="GoalkeeperTree", children=[bola_solta, defesa_comum])

    return root

class GoalkeeperCommonPosition(py_trees.behaviour.Behaviour):
    
    def __init__(self, robot: Bob, name: str = "GoalkeeperCommonPosition"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = Positioning_helper.get_object()
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:

        bm = BobManager.get_instance()
        position = bm.get_goalkeeper_defense_position(self.robot.state.robot_id)

        if position is None:
            return

        self.robot.state.target_pose = position
        self.robot.fast_movement()

        return py_trees.common.Status.SUCCESS


