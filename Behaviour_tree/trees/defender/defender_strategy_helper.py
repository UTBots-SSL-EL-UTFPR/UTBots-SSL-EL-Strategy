# Behaviour_tree/trees/defender/defender_strategy_helper.py
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from Behaviour_tree.helpers.motion_helper import MotionHelper
from utils.pose2D import Pose2D

class DefenderStrategyHelper:
    _ws = World_State.get_object()

    @classmethod
    def get_intercept_position(cls, robot_pos: Pose2D) -> Pose2D | None:
        """
        Calcula o ponto de interceptação usando uma projeção geométrica
        na trajetória da bola.
        """
        ball_pos = cls._ws.get_ball_position()
        ball_vel = cls._ws.get_ball_velocity() # A velocidade ainda é necessária para a DIREÇÃO

        if not ball_pos or not ball_vel:
            return None

        # Se a bola está parada, o alvo é a própria bola.
        if ball_vel.x**2 + ball_vel.y**2 < 10.0:
            return ball_pos

        # Usa o GeometryHelper para projetar a posição do robô na trajetória da bola
        intercept_point = GeometryHelper.project_point_on_line(
            point=robot_pos,
            line_origin=ball_pos,
            line_direction=ball_vel
        )
        
        return intercept_point

    @classmethod
    def get_blocking_position(cls) -> Pose2D:
        """Calcula a posição para bloquear um chute do oponente."""
        # TODO: Identificar qual oponente tem a bola
        opponent_pos = cls._ws.get_all_foes_position()[0] # Exemplo: pega o primeiro
        goal_center = FieldHelper.get_team_goal_center()
        
        # Posiciona-se na linha entre o oponente e o centro do gol
        return GeometryHelper.calculate_point_on_line(opponent_pos, goal_center, 200)

    @classmethod
    def get_zonal_marking_position(cls) -> Pose2D:
        """Calcula uma posição defensiva com base na posição da bola."""
        ball_pos = cls._ws.get_ball_position()
        goal_center = FieldHelper.get_team_goal_center()
        
        # Posiciona-se na linha entre a bola e o gol, mas recuado
        target = GeometryHelper.calculate_point_on_line(ball_pos, goal_center, 500)
        
        # Garante que o defensor não saia muito da frente do gol
        target.y = Pose2D._clamp(target.y, -1000, 1000)
        target.x = max(target.x, goal_center.x + 200)
        return target

    @classmethod
    def get_base_position(cls) -> Pose2D:
        """Retorna a posição defensiva padrão."""
        goal_center = FieldHelper.get_team_goal_center()
        return Pose2D(goal_center.x + 400, 0)
    
    @classmethod
    def get_path_to_target(cls, robot_pos: Pose2D, target_pos: Pose2D) -> list[Pose2D]:
        """Calcula o caminho até um alvo, desviando de obstáculos."""
        ball_pos = cls._ws.get_ball_position()
        obstacles = cls._ws.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot_pos]
        
        return MotionHelper.find_shortest_path(robot_pos, target_pos, obstacles, ball_pos)