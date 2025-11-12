# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #
from Behaviour_tree.core.World_State import World_State
from SSL_configuration.configuration import Configuration
from utils.pose2D import Pose2D

from .geometry_helper import GeometryHelper

# -------------------------------------------------------------------------- #
#                           CONSTANTES E CONFIGURAÇÃO                        #
# -------------------------------------------------------------------------- #

# Dimensões do campo (em milímetros, conforme SSL)
FIELD_WIDTH = 4500
FIELD_HEIGHT = 3000

FIELD_X_MIN = -FIELD_WIDTH / 2  # -2250
FIELD_X_MAX = FIELD_WIDTH / 2  #  2250
FIELD_Y_MIN = -FIELD_HEIGHT / 2  # -1500
FIELD_Y_MAX = FIELD_HEIGHT / 2  #  1500
HALF_GOALKEEPER_AREA_WIDTH = 675
GOAL_LENGHT = int(500)
WALL_MARGIN = int(200)
KEEPER_MARGIN = int(200)
GRID_STEP = int(250)
HALF_LEGHT = int(FIELD_WIDTH / 2)
HALF_WID = int(FIELD_HEIGHT / 2)

# +------------------------------------------------------------------------+ #
# |                             FieldHelper                                | #
# +------------------------------------------------------------------------+ #


class FieldHelper:

    GOAL_AREA_Y_LIMIT = int(700)
    GOAL_AREA_X_INNER_LIMIT = int(1600)
    GOAL_AREA_X_OUTER_LIMIT = int(2250)
    GOAL_Y_LIMIT = int(400)

    @classmethod
    def get_enemy_goal_center(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= -config.get_side_sign()
        return goal_pose

    @classmethod
    def get_team_goal_center(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= config.get_side_sign()
        return goal_pose

    @classmethod
    def get_out_goal(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2500, 0)
        goal_pose.x *= -config.get_side_sign()
        return goal_pose

    @classmethod
    def clamp_into_goalkeeper_area(cls, position: Pose2D) -> Pose2D:

        our_goal = cls.get_team_goal_center()
        new_x, new_y = position.x, position.y

        new_y = max(-cls.GOAL_AREA_Y_LIMIT, min(new_y, cls.GOAL_AREA_Y_LIMIT))

        if our_goal.x > 0:
            new_x = max(
                cls.GOAL_AREA_X_INNER_LIMIT, min(new_x, cls.GOAL_AREA_X_OUTER_LIMIT)
            )
        else:
            new_x = max(
                -cls.GOAL_AREA_X_OUTER_LIMIT, min(new_x, -cls.GOAL_AREA_X_INNER_LIMIT)
            )

        return Pose2D(int(new_x), int(new_y))

    @classmethod
    def get_most_advanced_opponent(cls):
        ws = World_State.get_object()
        x = cls.get_team_goal_center().x
        opponents = ws.get_all_foes_position()
        if not opponents:
            return None
        return max(opponents, key=lambda opp: opp.x * x)

    @classmethod
    def clamp_out_goalkeeper_area(cls, position: Pose2D) -> Pose2D:

        pos_x, pos_y = position.x, position.y

        in_pos_area = (
            cls.GOAL_AREA_X_INNER_LIMIT < pos_x < cls.GOAL_AREA_X_OUTER_LIMIT
            and -cls.GOAL_AREA_Y_LIMIT < pos_y < cls.GOAL_AREA_Y_LIMIT
        )

        in_neg_area = (
            -cls.GOAL_AREA_X_OUTER_LIMIT < pos_x < -cls.GOAL_AREA_X_INNER_LIMIT
            and -cls.GOAL_AREA_Y_LIMIT < pos_y < cls.GOAL_AREA_Y_LIMIT
        )

        if not in_pos_area and not in_neg_area:
            return position

        if in_pos_area:
            dist_to_inner_x = pos_x - cls.GOAL_AREA_X_INNER_LIMIT
            dist_to_outer_x = cls.GOAL_AREA_X_OUTER_LIMIT - pos_x
            dist_to_top_y = cls.GOAL_AREA_Y_LIMIT - pos_y
            dist_to_bottom_y = pos_y - (-cls.GOAL_AREA_Y_LIMIT)

            min_dist = min(
                dist_to_inner_x, dist_to_outer_x, dist_to_top_y, dist_to_bottom_y
            )

            if min_dist == dist_to_inner_x:
                return Pose2D(cls.GOAL_AREA_X_INNER_LIMIT, pos_y)
            elif min_dist == dist_to_outer_x:
                return Pose2D(cls.GOAL_AREA_X_OUTER_LIMIT, pos_y)
            elif min_dist == dist_to_top_y:
                return Pose2D(pos_x, cls.GOAL_AREA_Y_LIMIT)
            else:
                return Pose2D(pos_x, -cls.GOAL_AREA_Y_LIMIT)

        if in_neg_area:
            dist_to_inner_x = -cls.GOAL_AREA_X_INNER_LIMIT - pos_x
            dist_to_outer_x = pos_x - (-cls.GOAL_AREA_X_OUTER_LIMIT)
            dist_to_top_y = cls.GOAL_AREA_Y_LIMIT - pos_y
            dist_to_bottom_y = pos_y - (-cls.GOAL_AREA_Y_LIMIT)

            min_dist = min(
                dist_to_inner_x, dist_to_outer_x, dist_to_top_y, dist_to_bottom_y
            )

            if min_dist == dist_to_inner_x:
                return Pose2D(-cls.GOAL_AREA_X_INNER_LIMIT, pos_y)
            elif min_dist == dist_to_outer_x:
                return Pose2D(-cls.GOAL_AREA_X_OUTER_LIMIT, pos_y)
            elif min_dist == dist_to_top_y:
                return Pose2D(pos_x, cls.GOAL_AREA_Y_LIMIT)
            else:
                return Pose2D(pos_x, -cls.GOAL_AREA_Y_LIMIT)

        return position

    @classmethod
    def calculate_defense_line_x(cls, depth_factor: float) -> int:
        """
        Calcula a coordenada X da linha de defesa do goleiro.
        """
        goal_line_x = cls.get_team_goal_center().x
        defense_line_x_outer = (
            -cls.GOAL_AREA_X_INNER_LIMIT
            if goal_line_x < 0
            else cls.GOAL_AREA_X_INNER_LIMIT
        )
        return GeometryHelper.linear_interpolation(
            goal_line_x, defense_line_x_outer, depth_factor
        )

    @classmethod
    def get_team_goal_posts(cls) -> tuple[Pose2D, Pose2D]:
        """Retorna as posições da trave superior e inferior do nosso gol."""
        goal_x = cls.get_team_goal_center().x
        post_top = Pose2D(goal_x, cls.GOAL_Y_LIMIT)
        post_bottom = Pose2D(goal_x, -cls.GOAL_Y_LIMIT)
        return post_top, post_bottom

    @classmethod
    def get_attack_y_magnitude(cls) -> float:
        """Retorna a magnitude no eixo Y largura no ataque."""
        return 1200
