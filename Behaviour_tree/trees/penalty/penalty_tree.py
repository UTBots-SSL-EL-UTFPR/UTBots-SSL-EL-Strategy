"""
Penalty tree: verifica cenário de pênalti (stub), posiciona entre bola e gol, escolhe lado e chuta.
"""

from __future__ import annotations

import py_trees as pt

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.BobManager import BobManager
from utils.pose2D import Pose2D


def get_penalty_tree(robot: Bob) -> pt.behaviour.Behaviour:
    # Nó de sequência principal do pênalti
    is_penalty = IsPenalty(robot)
    position_between_ball_and_goal = PositionBetweenBallAndGoal(robot)
    choose_side_and_shoot = ChooseSideAndShoot(robot)

    root = pt.composites.Sequence(
        name="PenaltyTree",
        memory=False,
        children=[is_penalty, position_between_ball_and_goal, choose_side_and_shoot],
    )
    return root


class IsPenalty(pt.behaviour.Behaviour):
    """Stub: checagem de pênalti (deixe em branco por enquanto)."""

    def __init__(self, robot: Bob, name: str = "IsPenalty"):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()

    def update(self) -> pt.common.Status:
        # TODO: implementar detecção real de pênalti
        # Por enquanto, sempre SUCCESS para encadear os próximos passos
        return pt.common.Status.SUCCESS


class PositionBetweenBallAndGoal(pt.behaviour.Behaviour):
    """Posiciona o robô entre a bola e o gol adversário."""

    def __init__(self, robot: Bob, name: str = "PositionBetweenBallAndGoal"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        # Centro do gol adversário (assumindo eixo X positivo é ataque; ajuste se houver flag de lado)
        goal_center = Pose2D(2250, 0)

        # Posiciona num ponto alinhado bola->gol, a uma pequena margem da bola para chutar
        target = Pose2D.align_two(ball, goal_center, margin=200, is_left_team=True)
        self.robot.set_new_target_position(target)
        self.robot.fast_movement()
        return pt.common.Status.SUCCESS


class ChooseSideAndShoot(pt.behaviour.Behaviour):
    """Escolhe um lado do gol e chuta."""

    def __init__(self, robot: Bob, name: str = "ChooseSideAndShoot"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        # heurística simples: escolhe lado com maior y livre (placeholder)
        left_post = Pose2D(2250, 300)
        right_post = Pose2D(2250, -300)

        # Escolha simplificada: alterna pelo y da bola
        target = left_post if ball.y < 0 else right_post

        # Orienta e chuta
        self.robot.set_new_target_position(target)
        self.robot.fast_movement()
        self.robot.kick()
        return pt.common.Status.SUCCESS
