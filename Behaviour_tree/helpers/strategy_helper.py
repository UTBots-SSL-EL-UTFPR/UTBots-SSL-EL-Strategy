# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #

from typing import List

from Behaviour_tree.core.World_State import TeamID, World_State
from SSL_configuration.configuration import Configuration
from utils.defines import DISTANCE_PRESS_OPPONENT, MIN_PASS_DISTANCE
from utils.pose2D import Pose2D, Quadrant, QuadrantType, RoleType

from .field_helper import GRID_STEP, HALF_LEGHT, HALF_WID, FieldHelper
from .geometry_helper import GeometryHelper
from .motion_helper import MotionHelper
from .positioning_helper import PositioningHelper

# +------------------------------------------------------------------------+ #
# |                            StrategyHelper                              | #
# +------------------------------------------------------------------------+ #


class StrategyHelper:
    _ws = World_State.get_object()
    _config = Configuration.getObject()

    @classmethod
    def get_press_oponent_position(cls):
        ball_position = cls._ws.get_ball_position()
        goal_position = FieldHelper.get_team_goal_center()
        return GeometryHelper.calculate_point_on_line(
            ball_position, goal_position, DISTANCE_PRESS_OPPONENT
        )

    @classmethod
    def get_ball_recovery_position(cls):
        ball_position = cls._ws.get_ball_position()

        goal_position = FieldHelper.get_enemy_goal_center()
        return GeometryHelper.calculate_point_on_line(
            ball_position, goal_position, -DISTANCE_PRESS_OPPONENT
        )

    @classmethod
    def set_offensive_suport_position(cls, robot_position: Pose2D):
        """
        Calcula a posição do SUPORTE OFENSIVO de forma determinística, buscando
        o maior espaço com visibilidade tanto do cobrador quanto do gol.
        """
        robot_pos = robot_position

        opponents = cls._ws.get_all_foes_position()
        goal_center = FieldHelper.get_out_goal()
        ball_pos = cls._ws.get_ball_position()
        target_pose = robot_pos
        free_quadrants_enums = PositioningHelper.get_atack_quadrant_free(100)

        found_squares = {}
        for quad_enum in free_quadrants_enums:
            quad_obj = quad_enum.value
            visible_square = PositioningHelper.find_largest_dual_visibility_square(
                quadrant=quad_obj,
                origin_kicker=ball_pos,
                origin_goal=goal_center,
                opponents=opponents,
                grid_step=GRID_STEP,
            )

            if visible_square:
                found_squares[quad_enum] = visible_square

        priority_order = []
        if ball_pos.y <= 0:
            priority_order = [
                QuadrantType.Q4,
                QuadrantType.Q3,
                QuadrantType.Q12,
                QuadrantType.Q11,
                QuadrantType.Q8,
                QuadrantType.Q7,
            ]
        else:
            priority_order = [
                QuadrantType.Q12,
                QuadrantType.Q11,
                QuadrantType.Q4,
                QuadrantType.Q3,
                QuadrantType.Q8,
                QuadrantType.Q7,
            ]
        for priority_quad in priority_order:
            if priority_quad in found_squares:
                chosen_square = found_squares[priority_quad]

                safest_point = PositioningHelper.find_safest_point_in_square(
                    square=chosen_square,
                    kicker_pos=ball_pos,
                    ball_pos=ball_pos,
                    opponents=opponents,
                    min_pass_dist=MIN_PASS_DISTANCE,
                )
                if safest_point:
                    target_pose = Pose2D(
                        Pose2D._clamp(safest_point.x, -2050, 2050),
                        Pose2D._clamp(safest_point.y, -1300, 1300),
                    )
                    break

        return cls.get_Robot_path(target_pose, robot_pos, ball_pos)

    @classmethod
    def set_goalkeeper_position(cls, robot_pos: Pose2D):

        obstacles = cls._ws.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot_pos]

        target_pose = Pose2D(-100, 0)
        new_path = MotionHelper.find_shortest_path(
            robot_pos,
            target_pose,
            obstacles,
            cls._ws.get_ball_position(),
        )
        return new_path

    @classmethod
    def get_Robot_path(
        cls,
        target_pose: Pose2D,
        robot_position: Pose2D,
        ball_position: Pose2D | None = None,
    ):
        obstacles = cls._ws.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot_position]
        return MotionHelper.find_shortest_path(
            robot_position, target_pose, obstacles, ball_position
        )

    @classmethod
    def get_oriented_robot_path(
        cls,
        target_pose: Pose2D,
        robot_position: Pose2D,
        target_theta: float,
        ball_position: Pose2D | None = None,
    ):
        path = cls.get_Robot_path(target_pose, robot_position, ball_position)
        target_pose.theta = target_theta
        path[-1] = target_pose
        return path

    @classmethod
    def _decide_goalkeeper_depth_factor(cls, ball_position: Pose2D) -> float:
        """
        Decide o quão agressivo o goleiro deve ser.
        """
        goal_center = FieldHelper.get_team_goal_center()
        dist_ball_to_goal = abs(ball_position.x - goal_center.x)

        if dist_ball_to_goal < 800:
            return 0.8
        if dist_ball_to_goal < 1200:
            return 0.6
        return 0.1

    @classmethod
    def get_goalkeeper_defense_position(cls) -> Pose2D:
        """
        Executa a estratégia do goleiro para encontrar a melhor posição.
        """
        ball = cls._ws.get_ball_position()
        our_goal = FieldHelper.get_team_goal_center()

        if ball is None:
            return our_goal

        is_behind_goal = (our_goal.x < 0 and ball.x < our_goal.x) or (
            our_goal.x > 0 and ball.x > our_goal.x
        )
        if is_behind_goal:
            return FieldHelper.clamp_into_goalkeeper_area(our_goal)

        depth_factor = cls._decide_goalkeeper_depth_factor(ball)

        defense_x = FieldHelper.calculate_defense_line_x(depth_factor)

        post_top, post_bottom = FieldHelper.get_team_goal_posts()

        bisector_dir = GeometryHelper.calculate_bisector_direction(
            ball, post_top, post_bottom
        )

        ideal_target = GeometryHelper.find_line_intersection_with_vertical(
            start_point=ball, direction_vec=bisector_dir, vertical_line_x=defense_x
        )

        final_target = FieldHelper.clamp_into_goalkeeper_area(ideal_target)

        return final_target

    @classmethod
    def calculate_attack_support_pos(cls, ball_carrier_pose: Pose2D) -> Pose2D:
        """Calcula a melhor posição para se oferecer como opção de passe no ataque."""
        FORWARD_PASS_DISTANCE = 800
        SAFE_PASS_RECEPTION_DISTANCE = 400
        opponents = cls._ws.get_all_foes_position()

        target_y_magnitude = FieldHelper.get_attack_y_magnitude()
        opponent_goal = FieldHelper.get_enemy_goal_center()

        target_y_side = int(
            -target_y_magnitude if ball_carrier_pose.y >= 0 else target_y_magnitude
        )

        ideal_x = ball_carrier_pose.x + FORWARD_PASS_DISTANCE
        if ideal_x > opponent_goal.x - 500:
            ideal_x = opponent_goal.x - 500

        ideal_target_pose = Pose2D(ideal_x, target_y_side)

        is_safe = all(
            opp.distance_to(ideal_target_pose) > SAFE_PASS_RECEPTION_DISTANCE
            for opp in opponents
        )

        if is_safe:
            return ideal_target_pose
        else:
            for dx in [-300, 0, 300]:
                for dy in [-400, 0, 400]:
                    candidate_pos = Pose2D(
                        ideal_target_pose.x + dx, ideal_target_pose.y + dy
                    )
                    if all(
                        opp.distance_to(candidate_pos) > SAFE_PASS_RECEPTION_DISTANCE
                        for opp in opponents
                    ):
                        return candidate_pos

        return ideal_target_pose

    @classmethod
    def calculate_defense_support_pos(cls) -> Pose2D:
        """Calcula a melhor posição para interceptar um contra-ataque."""
        INTERCEPT_DISTANCE_FROM_OPPONENT = 600
        most_advanced_opponent = FieldHelper.get_most_advanced_opponent()
        if not most_advanced_opponent:
            return Pose2D(-500, 0)

        our_goal = FieldHelper.get_team_goal_center()
        target_pose = GeometryHelper.calculate_point_on_line(
            origin=most_advanced_opponent,
            target=our_goal,
            radius=INTERCEPT_DISTANCE_FROM_OPPONENT,
        )

        target_pose.theta = GeometryHelper.calculate_angle_between_points(
            start_point=target_pose, end_point=most_advanced_opponent
        )

        return target_pose
