from core.World_State import World_State

from SSL_configuration.configuration import Configuration

from .field_helper import FieldHelper
from .geometry_helper import GeometryHelper

DISTANCE_PRESS_OPPONENT = 200
DISTANCE_BALL_POSETION = 100


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
            goal_position, ball_position, DISTANCE_BALL_POSETION
        )

