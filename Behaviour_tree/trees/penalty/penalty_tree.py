"""
Penalty tree: usa o subárvore de chute existente e adiciona uma etapa opcional de condução
da bola para um ângulo melhor antes de chutar.
"""

from __future__ import annotations

import math
import py_trees as pt

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.commom_behaviours.sub_trees.kick_subtree import get_kick_subtree
from Behaviour_tree.commom_behaviours import actions as cb_actions
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.helpers.motion_helper import MotionHelper
from utils.pose2D import Pose2D
from utils.defines import PENALTY_DRIVE_ADVANCE_MM


def get_penalty_tree(robot: Bob) -> pt.trees.BehaviourTree:
    """Sequência de pênalti:
    1) Checa contexto de pênalti (stub por enquanto);
    2) Calcula alvo para conduzir a bola em melhor ângulo;
    3) Move até esse alvo (conduzindo);
    4) Reutiliza o subárvore de chute (alinha e chuta).
    """

    is_penalty = IsPenalty(robot)
    drive_ball = DriveBallToShootingAngle(robot)
    move = cb_actions.Move_node(robot)
    kick_subtree = get_kick_subtree(robot)

    root_seq = pt.composites.Sequence(
        name="PenaltyTree",
        memory=False,
        children=[is_penalty, drive_ball, move, kick_subtree],
    )
    tree = pt.trees.BehaviourTree(root_seq)
    tree.setup()
    return tree


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


class DriveBallToShootingAngle(pt.behaviour.Behaviour):
    """Calcula um ponto adiante da bola no melhor ângulo de visibilidade do gol
    e define esse ponto como alvo, permitindo conduzir a bola antes de chutar.
    """

    def __init__(self, robot: Bob, name: str = "DriveBallToShootingAngle", advance_mm: int = PENALTY_DRIVE_ADVANCE_MM):
        super().__init__(name)
        self.robot = robot
        self.advance_mm = advance_mm
        self._bb = Blackboard_Manager.get_instance()

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        ws = World_State.get_object()
        pos_helper = PositioningHelper.get_object()

        ball = ws.get_ball_position()
        if ball is None:
            return pt.common.Status.FAILURE

        kicker_pose = self.robot.state.position
        goal_pose = pos_helper.get_goal_center()
        obstacles = ws.get_all_robot_position()
        # remove o próprio robô da lista de obstáculos, se presente
        obstacles = [o for o in obstacles if o != kicker_pose]

        # melhor ângulo para chutar (considera goleiro e obstáculos)
        desired_angle = pos_helper.middle_goal_visibility_range(kicker_pose, goal_pose, obstacles)

        # alvo para conduzir a bola para frente nesse ângulo
        target_x = int(ball.x + self.advance_mm * math.cos(desired_angle))
        target_y = int(ball.y + self.advance_mm * math.sin(desired_angle))
        target = Pose2D(target_x, target_y, self.robot.state.position.theta)

        # define alvo e caminho; movimento será executado pelo Move_node seguinte
        self.robot.state.set_target_position(target)
        new_path = MotionHelper.find_shortest_path(kicker_pose, target, obstacles, ball)
        self.robot.set_path(new_path)
        return pt.common.Status.SUCCESS


    
