# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #

from Behaviour_tree.core.World_State import RobotID, World_State
from SSL_configuration.configuration import Configuration
from utils.defines import DISTANCE_PRESS_OPPONENT, MIN_PASS_DISTANCE
from utils.pose2D import Pose2D, Quadrant, QuadrantType, RoleType

from .field_helper import GRID_STEP, FieldHelper
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
        goal_position = FieldHelper.get_goal_center()
        return GeometryHelper.calculate_point_on_line(
            ball_position, goal_position, DISTANCE_PRESS_OPPONENT
        )

    @classmethod
    def get_ball_recovery_position(cls):
        ball_position = cls._ws.get_ball_position()
        goal_position = FieldHelper.get_goal_center()
        return GeometryHelper.calculate_point_on_line(
            goal_position, ball_position, DISTANCE_PRESS_OPPONENT
        )

    @classmethod
    def set_offensive_suport_position(cls, robot_position: Pose2D):
        """
        Calcula a posição do SUPORTE OFENSIVO de forma determinística, buscando
        o maior espaço com visibilidade tanto do cobrador quanto do gol.
        """
        robot_pos = robot_position

        opponents = cls._ws.get_all_foes_position()
        goal_center = FieldHelper.get_goal_center()
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
    def get_Robot_path(
        cls, target_pose: Pose2D, robot_position: Pose2D, ball_position: Pose2D
    ):
        obstacles = cls._ws.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot_position]
        return MotionHelper.find_shortest_path(
            robot_position, target_pose, obstacles, ball_position
        )
