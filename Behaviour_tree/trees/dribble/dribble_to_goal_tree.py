"""
Tree: FollowBallAndDribbleToGoal

Comportamento:
- Se tem posse da bola: planeja conduzir até o gol inimigo e anda (sem chutar).
- Caso contrário: posiciona-se para recuperar a bola e anda até o alvo.

Implementação reusa nós existentes:
- Condition: HasBall
- Actions: RecuperarBola (define target para recuperar), Move_node (executa deslocamento)

Adiciona um nó simples PlanDribbleToEnemyGoal que define o alvo como o centro do gol inimigo.
"""

from __future__ import annotations

import py_trees as pt

from Behaviour_tree.commom_behaviours import condition as cond
from Behaviour_tree.commom_behaviours import actions as act
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D


def get_follow_and_dribble_tree(robot: Bob) -> pt.trees.BehaviourTree:
    """Cria a árvore:
    Selector(
      Sequence(HasBall, PlanDribbleToEnemyGoal, Move_node),
      Sequence(RecuperarBola, Move_node)
    )
    """
    has_ball = cond.HasBall(robot)
    plan_dribble = PlanDribbleToEnemyGoal(robot)
    move = act.Move_node(robot)

    recover = act.RecuperarBola(robot)

    with_ball_seq = pt.composites.Sequence(
        name="WithBall_DribbleToGoal",
        memory=False,
        children=[has_ball, plan_dribble, move],
    )

    recover_seq = pt.composites.Sequence(
        name="RecoverBall_ThenMove",
        memory=False,
        children=[recover, move],
    )

    root = pt.composites.Selector(
        name="FollowBallAndDribbleToGoal",
        memory=False,
        children=[with_ball_seq, recover_seq],
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
        target = Pose2D(enemy_goal.x, enemy_goal.y, self.robot.state.position.theta)
        self.robot.set_new_target(target)
        return pt.common.Status.SUCCESS
