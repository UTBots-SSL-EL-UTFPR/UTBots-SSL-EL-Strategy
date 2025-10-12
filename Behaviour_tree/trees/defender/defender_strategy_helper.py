# Behaviour_tree/trees/defender/defender_strategy_helper.py
from Behaviour_tree.core.World_State import World_State, TeamID
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from utils.pose2D import Pose2D
from Behaviour_tree.robot.bob import Bob
from utils.defines import ROBOT_RADIUS 
import numpy as np
import math

BALL_AVOID_MARGIN = 1500.0  # mm de margem para não passar sobre a bola
APPROACH_OFFSET = 150.0

class DefenderStrategyHelper:
    _ws = World_State.get_object()
    

    @classmethod
    def get_base_position_by_id(cls, robot_id: TeamID) -> Pose2D:
        """
        Define posições base seguras para cada robô:
        - Goleiro: centralizado no gol
        - Defensores: próximos à área, deslocados para cima e para baixo
        """
        goal_center = FieldHelper.get_team_goal_center()

        # Direção do campo (lado do nosso gol)
        # Se o gol tem x < 0 → jogamos da esquerda para direita
        # Se o gol tem x > 0 → jogamos da direita para esquerda
        sign = 1 if goal_center.x < 0 else -1

        # Distância de segurança dentro do campo (500mm para dentro da área)
        offset_inside_field = 500

        # Posições base (ajustadas para dentro do campo)
        base_positions = {
            # Goleiro
            TeamID.Kamiji: Pose2D(goal_center.x + sign * offset_inside_field, 0),
            # Defensor superior
            TeamID.Argenton:   Pose2D(goal_center.x + sign * (offset_inside_field + 600), 800),
            # Defensor inferior
            TeamID.SabKawa:  Pose2D(goal_center.x + sign * (offset_inside_field + 600), -800),
        }

        # Retorna a posição correspondente ou uma posição padrão próxima ao gol
        return base_positions.get(robot_id, Pose2D(goal_center.x + sign * 500, 0))


    @classmethod
    def get_aggressive_marking_pose(cls) -> Pose2D | None:
        """
        Calcula uma POSE para se posicionar ENTRE a bola e nosso gol,
        e pré-compensa o ângulo para a "bússola invertida" do Bob.
        """
        ball_pos = cls._ws.get_ball_position()
        our_goal = FieldHelper.get_team_goal_center()
        opponent_goal = FieldHelper.get_enemy_goal_center()

        if not ball_pos:
            return None

        # 1. Calcula a posição do alvo (x, y)
        target_pos = GeometryHelper.calculate_point_on_line(
            origin=ball_pos,
            target=our_goal,
            radius= APPROACH_OFFSET
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
        final_target_angle = Pose2D.normalize_angle_to_pi(compensated_angle)

        return Pose2D(target_pos.x, target_pos.y, final_target_angle)
    
    @classmethod
    def get_aggressive_marking_pose_avoiding_ball(cls, current_robot_pose: Pose2D) -> Pose2D | None:
        """
        Retorna a posição segura para o robô se aproximar, desviando da bola,
        respeitando a distância mínima (APPROACH_OFFSET).
        """
        ball_pos = cls._ws.get_ball_position()
        if not ball_pos:
            return None

        # Vetores do robô para a bola e para o alvo final
        robot_vec = np.array([current_robot_pose.x, current_robot_pose.y])
        ball_vec = np.array([ball_pos.x, ball_pos.y])
        goal_vec = np.array([FieldHelper.get_team_goal_center().x, FieldHelper.get_team_goal_center().y])

        # Se a bola estiver no caminho e muito próxima
        if cls.bola_no_caminho(robot_vec, goal_vec, ball_vec, margem=APPROACH_OFFSET):
            # Calcula ponto lateral para desviar da bola
            safe_point = cls.ponto_de_desvio(robot_vec, goal_vec, ball_vec, offset=APPROACH_OFFSET)
            return Pose2D(safe_point[0], safe_point[1])
        else:
            # Posição padrão entre bola e gol, respeitando APPROACH_OFFSET
            return cls.get_aggressive_marking_pose()



    @staticmethod
    def bola_no_caminho(robot_pos, target_pos, ball_pos, margem=0.2):
        traj = target_pos - robot_pos
        traj_norm = traj / np.linalg.norm(traj)
        to_ball = ball_pos - robot_pos
        proj = np.dot(to_ball, traj_norm)
        if 0 < proj < np.linalg.norm(traj):
            lateral_dist = np.linalg.norm(to_ball - proj * traj_norm)
            return lateral_dist < margem
        return False

    @staticmethod
    def ponto_de_desvio(robot_pos, target_pos, ball_pos, offset=0.3):
        traj = target_pos - robot_pos
        traj_norm = traj / np.linalg.norm(traj)
        perp = np.array([-traj_norm[1], traj_norm[0]])
        if np.dot(perp, ball_pos - robot_pos) < 0:
            perp = -perp
        return ball_pos + perp * offset

    @classmethod
    def get_safe_marking_pose(cls, robot_pos: Pose2D, target_pos: Pose2D, ball_pos: Pose2D) -> Pose2D:
        """
        Retorna um ponto seguro:
        - Se a bola estiver no caminho, aplica um desvio lateral
        - Caso contrário, retorna o target original
        """
        traj = np.array([target_pos.x - robot_pos.x, target_pos.y - robot_pos.y])
        traj_dist = np.linalg.norm(traj)
        if traj_dist < 1e-3:
            return target_pos

        traj_norm = traj / traj_dist
        to_ball = np.array([ball_pos.x - robot_pos.x, ball_pos.y - robot_pos.y])
        proj = np.dot(to_ball, traj_norm)

        # Verifica se a bola está na trajetória do robô
        if 0 < proj < traj_dist:
            lateral_dist = np.linalg.norm(to_ball - proj * traj_norm)
            if lateral_dist < (ROBOT_RADIUS + BALL_AVOID_MARGIN):
                # Desvio lateral
                perp = np.array([-traj_norm[1], traj_norm[0]])
                if np.dot(perp, to_ball) < 0:
                    perp = -perp
                safe_point = np.array([ball_pos.x, ball_pos.y]) + perp * (ROBOT_RADIUS + BALL_AVOID_MARGIN)
                return Pose2D(safe_point[0], safe_point[1], target_pos.theta)

        # Caso a bola não esteja no caminho, retorna o alvo original
        return target_pos

    @classmethod
    def get_locked_rotation_pose(cls, anchor_point: Pose2D, ball_pos: Pose2D) -> Pose2D:
        """
        Retorna a pose com ângulo travado para rotacionar sempre mirando na bola.
        """
        if not ball_pos or not anchor_point:
            return anchor_point or Pose2D(0, 0, 0)

        dx = ball_pos.x - anchor_point.x
        dy = ball_pos.y - anchor_point.y
        angle = math.atan2(dy, dx)
        final_angle = Pose2D.normalize_angle_to_pi(angle)
        return Pose2D(anchor_point.x, anchor_point.y, final_angle)
    
    @classmethod
    def get_safe_target_pose(cls, robot_pose: Pose2D, lateral_offset: float = 300.0) -> Pose2D:
        """
        Calcula uma posição segura para o robô, desviando lateralmente da bola
        mantendo o alvo estratégico atualizado (entre bola e nosso gol).
        
        - robot_pose: Pose2D atual do robô
        - lateral_offset: distância lateral para contornar a bola
        """
        ball_pos = cls._ws.get_ball_position()
        if not ball_pos:
            return cls.get_aggressive_marking_pose()  # fallback

        strategic_target = cls.get_aggressive_marking_pose()
        if not strategic_target:
            return robot_pose  # fallback

        # Vetor do robô para o alvo
        traj_vec = np.array([strategic_target.x - robot_pose.x,
                            strategic_target.y - robot_pose.y])
        traj_norm = traj_vec / (np.linalg.norm(traj_vec) + 1e-6)

        # Vetor perpendicular (direção lateral)
        perp = np.array([-traj_norm[1], traj_norm[0]])

        # Define o lado correto para desviar: sempre do mesmo lado da linha bola→alvo
        ball_to_target = np.array([strategic_target.x - ball_pos.x,
                                strategic_target.y - ball_pos.y])
        if np.cross(traj_norm, ball_to_target) < 0:
            perp = -perp

        # Calcula posição segura lateral
        safe_x = ball_pos.x + perp[0] * lateral_offset
        safe_y = ball_pos.y + perp[1] * lateral_offset

        # Ângulo final mirando a bola
        angle_to_ball = math.atan2(ball_pos.y - safe_y, ball_pos.x - safe_x)
        final_angle = Pose2D.normalize_angle_to_pi(angle_to_ball)

        return Pose2D(safe_x, safe_y, final_angle)
    
    @classmethod
    def get_safe_target_pose_between_ball_and_our_goal(cls, robot_pose: Pose2D, lateral_offset: float = 200.0) -> Pose2D:
        """
        Retorna a posição segura do robô entre bola e nosso gol,
        mantendo uma distância mínima lateral da bola usando a função base.
        """
        # Primeiro pega o alvo estratégico original (entre bola e gol)
        strategic_pose = cls.get_safe_target_pose(robot_pose, lateral_offset=0)

        ball_pos = cls._ws.get_ball_position()
        if not ball_pos:
            return strategic_pose  # fallback

        # Vetor do robô para o alvo estratégico
        traj_vec = np.array([strategic_pose.x - robot_pose.x,
                            strategic_pose.y - robot_pose.y])
        traj_norm = traj_vec / (np.linalg.norm(traj_vec) + 1e-6)

        # Vetor perpendicular para desvio lateral
        perp = np.array([-traj_norm[1], traj_norm[0]])

        # Decide o lado correto para desviar
        ball_to_target = np.array([strategic_pose.x - ball_pos.x,
                                strategic_pose.y - ball_pos.y])
        if np.cross(traj_norm, ball_to_target) < 0:
            perp = -perp

        # Ponto final seguro com desvio lateral
        safe_x = ball_pos.x + perp[0] * lateral_offset
        safe_y = ball_pos.y + perp[1] * lateral_offset

        # Ângulo mirando a bola
        angle_to_ball = math.atan2(ball_pos.y - safe_y, ball_pos.x - safe_x)
        final_angle = Pose2D.normalize_angle_to_pi(angle_to_ball)

        return Pose2D(safe_x, safe_y, final_angle)






