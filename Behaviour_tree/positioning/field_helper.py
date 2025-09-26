from SSL_configuration.configuration import Configuration
from utils.pose2D import Pose2D


class FieldHelper:

    @classmethod
    def get_goal_center(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= config.get_side_sign()
        return goal_pose
