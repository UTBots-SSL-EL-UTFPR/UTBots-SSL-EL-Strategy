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
from Behaviour_tree.helpers.field_helper import FIELD_X_MAX, FIELD_X_MIN, HALF_LEGHT
from utils.pose2D import QuadrantType, RoleType, ZoneType
from utils.defines import (
    BALL_RADIUS,
    FIELD_INVERTED_SIDE,
    ROBOT_RADIUS,
)
from utils.pose2D import Pose2D

from ...core.event_callbacks import BlackboardKeys
from ...core.World_State import TeamID, World_State

navigation_flags = BlackboardKeys.Flags.Navigation
positions = BlackboardKeys.Values.Positions
team_flags = BlackboardKeys.Flags.TeamContext
import time
from typing import Optional, Tuple

import py_trees as pt

from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob

from ...helpers import positioning_helper as Positioning_helper

# ---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
# ---------------------------------------------------------------------------------------#
logger = logging.getLogger(__name__)


class DefenderActions(pt.behaviour.Behaviour):
    """
    Classe que define ações específicas para o defensor.
    """

    def __init__(self, name: str, blackboard: Blackboard_Manager):
        super().__init__(name)
        self.blackboard = blackboard
        self.world_state = World_State.get_object()
        self.positioning_helper = PositioningHelper.get_object()
        self.logger = logging.getLogger(__name__)

    def update(self):
        # Implementação do método abstrato
        pass
    
    def set_defensive_position(self, robot_id: TeamID):
        """
        Posiciona o defensor para proteger a área defensiva.

        Estratégia:
        - Mantém o defensor entre a bola e o gol.
        - Restringe o movimento ao lado defensivo do campo.
        """
        robot = self.blackboard.get_robot(robot_id)
        if robot is None or robot.state is None:
            return None

        ball = self.world_state.get_ball_position()
        if ball is None:
            return None

        # Define a área defensiva
        area_x_min, area_x_max = -2250, -1000
        area_y_min, area_y_max = -1300, 1300

        # Calcula a posição alvo do defensor
        target_x = max(area_x_min, min(ball.x - 300, area_x_max))
        target_y = max(area_y_min, min(ball.y, area_y_max))

        target_pose = Pose2D(target_x, target_y)

        # Planejamento de caminho
        obstacles = self.world_state.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot.state.position]
        robot.state.path = robot.find_shortest_path(
            robot.state.position,
            target_pose,
            obstacles,
            ROBOT_RADIUS,
            ball,
            BALL_RADIUS,
        )
        robot.state.role = RoleType.DEFENDER

        self.logger.info(f"Defensor {robot_id} posicionado em {target_pose}")
        return target_pose

    def intercept_ball(self, robot_id: TeamID):
        """
        Posiciona o defensor para interceptar a bola.

        Estratégia:
        - Calcula a trajetória da bola.
        - Move o defensor para um ponto na trajetória da bola.
        """
        robot = self.blackboard.get_robot(robot_id)
        if robot is None or robot.state is None:
            return None

        ball = self.world_state.get_ball_position()
        ball_velocity = self.world_state.get_ball_velocity()

        if ball is None or ball_velocity is None:
            return None

        # Calcula o ponto de interceptação
        intercept_point = self.positioning_helper.calculate_interception_point(
            ball, ball_velocity, robot.state.position
        )

        # Planejamento de caminho
        obstacles = self.world_state.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot.state.position]
        robot.state.path = robot.find_shortest_path(
            robot.state.position,
            intercept_point,
            obstacles,
            ROBOT_RADIUS,
            ball,
            BALL_RADIUS,
        )
        robot.state.role = RoleType.DEFENDER

        self.logger.info(f"Defensor {robot_id} interceptando bola em {intercept_point}")
        return intercept_point
