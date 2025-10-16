"""
Halt tree: quase um STOP. Faz os robôs irem para uma posição padrão de defesa,
movendo devagar, e mantendo pelo menos 50cm longe da bola.
"""

from __future__ import annotations

import py_trees as pt

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from utils.defines import HALT_SLOW_SPEED

SAFE_BALL_DISTANCE = int(500)  # 50 cm em milímetros (projeto usa mm)


def get_halt_tree(robot: Bob) -> pt.trees.BehaviourTree:
    """Arvore: GoToDefaultDefensePos (lento e 50cm da bola)."""
    goto_default_defense = GoToDefaultDefensePos(robot)
    root = pt.composites.Sequence(
        name="HaltTree", memory=False, children=[goto_default_defense]
    )
    tree = pt.trees.BehaviourTree(root)
    tree.tick()
    return tree


class GoToDefaultDefensePos(pt.behaviour.Behaviour):
    """
    - Define uma posição padrão de defesa simples (placeholder).
    - Anda em velocidade lenta até essa posição.
    - Garante ficar a pelo menos 50cm da bola.
    """

    def __init__(self, robot: Bob, name: str = "GoToDefaultDefensePos"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        # Posição padrão de defesa (placeholder): um pouco atrás da bola no eixo X
        # Ajuste conforme seu lado de campo e layout defensivo desejado
        target = Pose2D(ball.x - 300, ball.y)

        # Garante distância mínima de 50cm da bola
        if target.distance_to(ball) < SAFE_BALL_DISTANCE:
            # empurra para trás mantendo direção
            dx = target.x - ball.x
            dy = target.y - ball.y
            norm = (dx * dx + dy * dy) ** 0.5 or 1.0
            target = Pose2D(
                int(ball.x + (dx / norm) * SAFE_BALL_DISTANCE),
                int(ball.y + (dy / norm) * SAFE_BALL_DISTANCE)
            )

        # Movimento lento: se houver API para setar velocidade, use; caso não, use um modo lento
        if hasattr(self.robot, "set_slow_speed"):
            try:
                self.robot.set_slow_speed(HALT_SLOW_SPEED)
            except Exception:
                pass

        # Define alvo e executa
        self.robot.set_new_target(target)
        # Se existir um método específico para movimento lento, preferir; senão usar fast_movement como placeholder
        if hasattr(self.robot, "slow_movement"):
            self.robot.slow_movement()
        else:
            self.robot.fast_movement()

        return pt.common.Status.SUCCESS
