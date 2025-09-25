from typing import Any

import py_trees
from py_trees.common import Status

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

ball_flags = BlackboardKeys.Flags.motion.ball
positions_values = BlackboardKeys.Values.Positions
team_flags = BlackboardKeys.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()
_pos_helper = Positioning_helper.get_object()

# =======================================================================================#
#                                     IMPLEMENTADOS                                     #
# =======================================================================================#


# =======================================================================================#
#                                         x                                             #
# =======================================================================================#


class Ball_in_defensive_area(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está na área defensiva.
    """

    def __init__(self, name: str = "Ball_in_defensive_area"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        ball_position = _bb.get("ball_position")
        if not ball_position:
            return py_trees.common.Status.FAILURE

        # Define os limites da área defensiva
        area_x_min, area_x_max = -2250, -1000
        area_y_min, area_y_max = -1300, 1300

        if (
            area_x_min <= ball_position.x <= area_x_max
            and area_y_min <= ball_position.y <= area_y_max
        ):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Opponent_in_danger_zone(py_trees.behaviour.Behaviour):
    """
    Verifica se um oponente está em uma zona perigosa próxima ao gol.
    """

    def __init__(self, name: str = "Opponent_in_danger_zone"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        opponents = _bb.get("opponents_positions")
        if not opponents:
            return py_trees.common.Status.FAILURE

        # Define os limites da zona perigosa
        danger_x_min, danger_x_max = -2250, -1500
        danger_y_min, danger_y_max = -800, 800

        for opponent in opponents:
            if (
                danger_x_min <= opponent.x <= danger_x_max
                and danger_y_min <= opponent.y <= danger_y_max
            ):
                return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Opponent_has_ball_in_danger_zone(py_trees.behaviour.Behaviour):
    """
    Verifica se um oponente na zona perigosa está com a posse da bola.
    """

    def __init__(self, name: str = "Opponent_has_ball_in_danger_zone"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        opponents = _bb.get("opponents_positions")
        if not opponents:
            return py_trees.common.Status.FAILURE

        # Define os limites da zona perigosa
        danger_x_min, danger_x_max = -2250, -1500
        danger_y_min, danger_y_max = -800, 800

        for opponent in opponents:
            if (
                danger_x_min <= opponent.x <= danger_x_max
                and danger_y_min <= opponent.y <= danger_y_max
            ):
                # Verifica se o oponente possui a bola
                if _bb.get(f"{opponent.id}{ball_flags.has_ball}"):
                    return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE


class Ball_moving_towards_goal(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está se movendo em direção ao gol.
    """

    def __init__(self, name: str = "Ball_moving_towards_goal"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        ball_velocity = _bb.get("ball_velocity")
        ball_position = _bb.get("ball_position")
        if not ball_velocity or not ball_position:
            return py_trees.common.Status.FAILURE

        # Verifica se a bola está se movendo na direção do gol
        if ball_velocity.x < 0 and -2250 <= ball_position.x <= -1000:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
