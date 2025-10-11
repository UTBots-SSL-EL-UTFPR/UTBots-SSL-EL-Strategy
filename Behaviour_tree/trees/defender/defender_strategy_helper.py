# Behaviour_tree/trees/defender/defender_strategy_helper.py
from Behaviour_tree.core.World_State import World_State, TeamID
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from utils.pose2D import Pose2D
import math

APPROACH_OFFSET = 150.0

class DefenderStrategyHelper:
    _ws = World_State.get_object()

    @classmethod
    def get_base_position_by_id(cls, robot_id: TeamID) -> Pose2D:
        # (Esta função não muda)
        goal_center = FieldHelper.get_team_goal_center()
        sign = -1 if goal_center.x < 0 else 1
        base_positions = {
            TeamID.Argenton: Pose2D(goal_center.x + (sign * 600), 0),
            TeamID.Kamiji:   Pose2D(goal_center.x + (sign * 1000), 1000),
            TeamID.SabKawa:  Pose2D(goal_center.x + (sign * 1000), -1000)
        }
        return base_positions.get(robot_id, Pose2D(goal_center.x + (sign * 600), 0))

    @classmethod
    def get_aggressive_marking_pose(cls) -> Pose2D | None:
        """
        Calcula uma POSE para se posicionar ENTRE a bola e nosso gol,
        e pré-compensa o ângulo para o controlador do Bob.
        """
        ball_pos = cls._ws.get_ball_position()
        our_goal = FieldHelper.get_team_goal_center()
        opponent_goal = FieldHelper.get_enemy_goal_center()

        if not ball_pos:
            return None

        # 1. Calcula a posição do alvo (x, y) - esta parte está correta
        target_pos = GeometryHelper.calculate_point_on_line(
            origin=ball_pos,
            target=our_goal,
            radius=APPROACH_OFFSET
        )

        # 2. Calcula o ângulo real desejado (virado para o gol adversário)
        real_angle = math.atan2(
            opponent_goal.y - ball_pos.y,
            opponent_goal.x - ball_pos.x
        )
        
        # ============================================================================== #
        # CORREÇÃO DEFINITIVA: A Pré-Compensação
        # Adicionamos 180 graus (math.pi) ao ângulo real para "traduzir" o alvo
        # para o "idioma" que o controlador do Bob entende.
        # ============================================================================== #
        compensated_angle = real_angle + math.pi
        
        # Normalizamos o ângulo para garantir que ele fique no intervalo [-pi, +pi]
        final_target_angle = compensated_angle#Pose2D.normalize_angle_to_pi(compensated_angle)

        return Pose2D(target_pos.x, target_pos.y, final_target_angle)