# Behaviour_tree/trees/defender/defender_strategy_helper.py
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from Behaviour_tree.helpers.motion_helper import MotionHelper
from utils.pose2D import Pose2D

BLOCKING_DISTANCE = 400.0
POSSESSION_THRESHOLD = 350.0
# ADIÇÃO: Distância mínima segura de qualquer oponente
MIN_SAFE_DISTANCE_FROM_OPPONENT = 300.0

class DefenderStrategyHelper:
    _ws = World_State.get_object()

    @classmethod
    def get_smart_defensive_position(cls) -> Pose2D | None:
        """
        Calcula o alvo defensivo e garante que ele seja seguro antes de retornar.
        """
        ball_pos = cls._ws.get_ball_position()
        opponents = cls._ws.get_all_foes_position()

        if not ball_pos:
            return cls.get_base_position()

        # 1. Calcula o alvo estratégico "ideal"
        raw_target = None
        closest_foe = min(opponents, key=lambda foe: foe.distance_to(ball_pos), default=None) if opponents else None

        if closest_foe and closest_foe.distance_to(ball_pos) < POSSESSION_THRESHOLD:
            raw_target = cls.get_blocking_position(opponent_pos=closest_foe)
        else:
            raw_target = cls.get_zonal_marking_position(ball_pos=ball_pos)

        # ============================================================================== #
        # 2. VALIDAÇÃO DE SEGURANÇA: Garante que o alvo não está dentro de um oponente.
        # ============================================================================== #
        if raw_target and opponents:
            for foe in opponents:
                if raw_target.distance_to(foe) < MIN_SAFE_DISTANCE_FROM_OPPONENT:
                    # Se o alvo está muito perto, afasta ele na linha a partir do oponente.
                    # Isso cria um novo alvo seguro na mesma direção.
                    raw_target = GeometryHelper.calculate_point_on_line(
                        origin=foe,
                        target=raw_target,
                        radius=MIN_SAFE_DISTANCE_FROM_OPPONENT
                    )
        
        return raw_target

    @classmethod
    def get_blocking_position(cls, opponent_pos: Pose2D) -> Pose2D:
        goal_center = FieldHelper.get_team_goal_center()
        return GeometryHelper.calculate_point_on_line(origin=opponent_pos, target=goal_center, radius=BLOCKING_DISTANCE)

    @classmethod
    def get_zonal_marking_position(cls, ball_pos: Pose2D) -> Pose2D:
        goal_center = FieldHelper.get_team_goal_center()
        target = GeometryHelper.calculate_point_on_line(ball_pos, goal_center, 500)
        target.y = Pose2D._clamp(target.y, -1000, 1000)
        target.x = max(target.x, goal_center.x + 200)
        return target

    # --- Funções que não mudam ---
    @classmethod
    def get_intercept_position(cls, robot_pos: Pose2D) -> Pose2D | None:
        ball_pos = cls._ws.get_ball_position()
        ball_vel = cls._ws.get_ball_velocity()
        if not ball_pos or not ball_vel or ball_vel.magnitude_sq() < 10.0: return None
        return GeometryHelper.project_point_on_line(point=robot_pos, line_origin=ball_pos, line_direction=ball_vel)

    @classmethod
    def get_base_position(cls) -> Pose2D:
        goal_center = FieldHelper.get_team_goal_center()
        return Pose2D(goal_center.x + 400, 0)
    
    @classmethod
    def get_path_to_target(cls, robot_pos: Pose2D, target_pos: Pose2D) -> list[Pose2D]:
        ball_pos = cls._ws.get_ball_position()
        obstacles = [obs for obs in cls._ws.get_all_robot_position() if obs != robot_pos]
        return MotionHelper.find_shortest_path(robot_pos, target_pos, obstacles, ball_pos)