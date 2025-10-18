"""
Tree: FollowBallAndDribbleToGoal

Comportamento:
- Se tem posse da bola: planeja conduzir até o gol inimigo e anda (sem chutar).
- Caso contrário: posiciona-se para recuperar a bola e anda até o alvo.

Implementação reusa nós existentes:
- Condition: HasBall
- Actions: Move_node (executa deslocamento)

Adiciona nós simples de planejamento direto para a bola e para o gol inimigo.
"""

from __future__ import annotations

import math

import py_trees as pt

from Behaviour_tree.commom_behaviours import actions as act
from Behaviour_tree.commom_behaviours import condition as cond
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D


def get_follow_and_dribble_tree(robot: Bob) -> pt.trees.BehaviourTree:
    """Monta a árvore que busca a bola em linha reta e, com posse, conduz até o gol."""
    has_ball_for_goal = cond.HasBall(robot, name="HasBall_GoalPush")
    plan_dribble = PlanDribbleToEnemyGoal(robot)
    move_to_goal = act.Move_node(robot, name="MoveToGoal")

    plan_ball = PlanStraightToBall(robot)
    move_to_ball = act.Move_node(robot, name="MoveToBall")

    with_ball_seq = pt.composites.Sequence(
        name="WithBall_DribbleToGoal",
        memory=False,
        children=[has_ball_for_goal, plan_dribble, move_to_goal],
    )

    chase_ball_seq = pt.composites.Sequence(
        name="ChaseBallDirectly",
        memory=False,
        children=[plan_ball, move_to_ball],
    )

    root = pt.composites.Selector(
        name="FollowBallAndDribbleToGoal",
        memory=False,
        children=[with_ball_seq, chase_ball_seq],
    )

    tree = pt.trees.BehaviourTree(root)
    tree.setup()
    return tree


class PlanDribbleToEnemyGoal(pt.behaviour.Behaviour):
    """Define o alvo para condução como o centro do gol inimigo.
    Não chuta; delega o deslocamento ao Move_node subsequente.
    """

    def __init__(self, robot: Bob, name: str = "PlanDribbleToEnemyGoal"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        enemy_goal = FieldHelper.get_enemy_goal_center()
        current_pos = getattr(self.robot.state, "position", None)
        heading = 0.0
        if current_pos is not None:
            heading = math.atan2(enemy_goal.y - current_pos.y, enemy_goal.x - current_pos.x)

        target = Pose2D(enemy_goal.x, enemy_goal.y, heading)
        self.robot.set_new_target(target)
        return pt.common.Status.SUCCESS


class PlanStraightToBall(pt.behaviour.Behaviour):
    """Planeja uma trajetória direta até a bola."""

    def __init__(self, robot: Bob, name: str = "PlanStraightToBall"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        ball_pose = self.robot.state.world_state.get_ball_position()
        current_pos = getattr(self.robot.state, "position", None)

        if ball_pose is None or current_pos is None:
            return pt.common.Status.FAILURE

        heading = math.atan2(ball_pose.y - current_pos.y, ball_pose.x - current_pos.x)
        target = Pose2D(ball_pose.x, ball_pose.y, heading)
        self.robot.set_new_target(target)
        return pt.common.Status.SUCCESS
