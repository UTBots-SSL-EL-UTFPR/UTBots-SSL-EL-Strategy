# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #
from SSL_configuration.configuration import Configuration
from utils.pose2D import Pose2D

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
GOAL_LENGHT = 500
WALL_MARGIN = 200
KEEPER_MARGIN = 200
GRID_STEP = 250
HALF_LEGHT = int(FIELD_WIDTH / 2)
HALF_WID = int(FIELD_HEIGHT / 2)


# +------------------------------------------------------------------------+ #
# |                             FieldHelper                                | #
# +------------------------------------------------------------------------+ #


class FieldHelper:

    @classmethod
    def get_enemy_goal_center(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= config.get_side_sign()
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
