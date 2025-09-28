# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #

import math

from utils.pose2D import Pose2D

# +------------------------------------------------------------------------+ #
# |                            GeometryHelper                              | #
# +------------------------------------------------------------------------+ #


class GeometryHelper:
    @staticmethod
    def calculate_point_on_line(
        origin: Pose2D, target: Pose2D, radius: float
    ) -> Pose2D:
        vec_x = target.x - origin.x
        vec_y = target.y - origin.y

        distance = math.hypot(vec_x, vec_y)

        if distance == 0:
            return origin
        unit_vec_x = vec_x / distance
        unit_vec_y = vec_y / distance
        new_x = origin.x + unit_vec_x * radius
        new_y = origin.y + unit_vec_y * radius

        return Pose2D(int(new_x), int(new_y))
