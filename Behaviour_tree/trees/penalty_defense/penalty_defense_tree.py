"""
Penalty defense tree: checa pênalti (stub), alinha na linha do gol com a bola e segue a bola sem sair da linha.
"""

from __future__ import annotations

import py_trees as pt

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FIELD_X_MAX, FIELD_X_MIN
from Behaviour_tree.robot.bob import Bob
from utils.defines import FIELD_INVERTED_SIDE
from utils.pose2D import Pose2D


def get_penalty_defense_tree(robot: Bob) -> pt.trees.BehaviourTree:
    is_penalty = IsPenalty(robot)
    align_on_goal_line = AlignOnGoalLine(robot)
    track_ball_on_goal_line = TrackBallOnGoalLine(robot)

    tree = pt.composites.Sequence(
        name="PenaltyDefenseTree",
        memory=False,
        children=[is_penalty, align_on_goal_line, track_ball_on_goal_line],
    )
    root = pt.trees.BehaviourTree(tree)
    root.setup()
    return root


class IsPenalty(pt.behaviour.Behaviour):
    """Stub: checagem de pênalti (deixe em branco por enquanto)."""

    def __init__(self, robot: Bob, name: str = "IsPenalty"):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()

    def update(self) -> pt.common.Status:
        # TODO: implementar detecção real de pênalti de defesa
        return pt.common.Status.SUCCESS


class AlignOnGoalLine(pt.behaviour.Behaviour):
    """Posiciona o robô na linha do gol, alinhado com o Y da bola."""

    def __init__(self, robot: Bob, name: str = "AlignOnGoalLine"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        # X da linha do nosso gol conforme o lado
        goal_x = FIELD_X_MAX if FIELD_INVERTED_SIDE else FIELD_X_MIN
        # Mantém na linha do gol, clampa Y dentro da trave (~ +/- 600mm)
        target = Pose2D(goal_x, Pose2D._clamp(ball.y, -600, 600))
        self.robot.set_new_target(target)
        self.robot.fast_movement()
        return pt.common.Status.SUCCESS


class TrackBallOnGoalLine(pt.behaviour.Behaviour):
    """Segue a bola ao longo da linha do gol, sem sair dela."""

    def __init__(self, robot: Bob, name: str = "TrackBallOnGoalLine"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        # Mantém o X fixo na linha do gol e segue apenas o Y da bola
        goal_x = FIELD_X_MAX if FIELD_INVERTED_SIDE else FIELD_X_MIN
        target = Pose2D(goal_x, Pose2D._clamp(ball.y, -600, 600))
        self.robot.set_new_target(target)
        self.robot.fast_movement()
        return pt.common.Status.SUCCESS
