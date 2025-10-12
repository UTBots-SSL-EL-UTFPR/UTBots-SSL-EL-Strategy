"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""

from __future__ import annotations

import logging
import math
import time
from time import sleep

import py_trees

from Behaviour_tree.managers.bob_manager import BobManager
from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID, World_State

navigation_flags = BlackboardKeys.Flags.motion.navigation
positions = BlackboardKeys.Values.Positions
team_flags = BlackboardKeys.Flags.Team_Flags
import time
from typing import Optional, Tuple

import py_trees as pt

team_flags = BlackboardKeys.Flags.Team_Flags
from commom_behaviours.actions import MovimentoUnico, RecuperarBola
from commom_behaviours.condition import FoesHaveBall, HasBall

from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob

from ...helpers import positioning_helper as Positioning_helper

# ---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
# ---------------------------------------------------------------------------------------#
logger = logging.getLogger(__name__)


def get_goalkeeper_tree(robot: Bob) -> pt.behaviour.Behaviour:


    #caso de bola solta e suas folhas=======================================
    recuperar_bola = RecuperarBola(robot, name="RecuperarBola")
    movimento_unico = MovimentoUnico(robot, name="MovimentoUnico")

    bola_solta = py_trees.composites.Sequence(
        name="Bola_Solta", memory=False, children=[recuperar_bola, movimento_unico]
    )

    #caso de defesa comum e suas folhas======================================
    foesHasBall = FoesHaveBall()
    goalkeeperCommonPosition = GoalkeeperCommonPosition(robot)

    defesa_comum = py_trees.composites.Sequence(
        name="Defesa_Comum",
        memory=False,
        children=[foesHasBall, goalkeeperCommonPosition],
    )

    #caso Ultimo Homem e suas folhas=========================================
    checkLastMan = CheckLastMan(robot)
    follow_ball = followBall(robot)

    ultimo_homem = py_trees.composites.Sequence(
        name="Ultimo_Homem",
        memory=False,
        children=[checkLastMan, follow_ball],
    )

    #tem a bola==============================================================
    passe_obj = passe(robot)
    chutar = chute(robot)
    hasBall = HasBall()

    tem_a_bola = py_trees.composites.Sequence(
        name="Tem_a_Bola", memory=False, children=[hasBall, passe_obj, chutar]
    )

    #Raiz da arvore==========================================================
    root = py_trees.composites.Selector(
        name="GoalkeeperTree", children=[bola_solta, defesa_comum, ultimo_homem, tem_a_bola]
    )

    return root


class GoalkeeperCommonPosition(py_trees.behaviour.Behaviour):

    def __init__(self, robot: Bob, name: str = "GoalkeeperCommonPosition"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:

        bm = BobManager.get_instance()
        position = bm.set_goalkeeper_defense_position(self.robot.state.robot_id)

        if position is None:
            return

        self.robot.state.target_position = position
        self.robot.fast_movement()

        return py_trees.common.Status.SUCCESS

class CheckLastMan(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "CheckLastMan"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        bm = BobManager.get_instance()
        if bm.get_last_man_id() != None:
            
            if bm.get_last_man_id() == self.robot.state.robot_id:
                return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE

class followBall(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "followBall"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """
        Faz o robô andar reto na direção da bola.
        """
        # Pega a posição atual da bola do mundo
        world_state = World_State.get_object()
        ball_position = world_state.get_ball_position()
        
        if ball_position is None:
            # Se não conseguir pegar a posição da bola, falha
            return py_trees.common.Status.FAILURE
        
        # Define a posição da bola como alvo
        self.robot.set_new_target(ball_position)
        
        # Usa movimento rápido para ir direto na direção da bola
        self.robot.fast_movement()
        
        return py_trees.common.Status.SUCCESS

class passe(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "passear"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        ...

class chute(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "chutar"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        ...


