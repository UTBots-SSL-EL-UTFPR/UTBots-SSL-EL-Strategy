# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #

import math

from utils.pose2D import Pose2D


# +------------------------------------------------------------------------+ #
# |                            GeometryHelper                              | #
# +------------------------------------------------------------------------+ #
class Vector2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)


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

    @classmethod
    def normalize_angle(cls, angle: float) -> float:
        """
        Normaliza ângulo para o intervalo [-pi, pi].
        """
        return (angle + math.pi) % (2 * math.pi) - math.pi

    @classmethod
    def angle_difference(cls, a: float, b: float) -> float:
        """
        Diferença angular entre `a` e `b`, resultado em [-pi, pi].
        """
        return cls.normalize_angle(a - b)

    @classmethod
    def is_angle_aligned(cls, a: float, b: float, tolerance: float) -> bool:
        """
        Verifica se dois ângulos estão alinhados dentro da tolerância.
        """
        return abs(cls.angle_difference(a, b)) <= tolerance

    @staticmethod
    def calculate_bisector_direction(
        origin: Pose2D, target1: Pose2D, target2: Pose2D
    ) -> Vector2D:
        """
        Calcula o vetor de direção do bissetor de um ângulo.
        """
        vec_to_target1 = Vector2D(
            target1.x - origin.x, target1.y - origin.y
        ).normalize()
        vec_to_target2 = Vector2D(
            target2.x - origin.x, target2.y - origin.y
        ).normalize()

        bisector_vec = (vec_to_target1 + vec_to_target2).normalize()
        return bisector_vec

    @staticmethod
    def find_line_intersection_with_vertical(
        start_point: Pose2D, direction_vec: Vector2D, vertical_line_x: int
    ) -> Pose2D:
        """
        Encontra a interseção entre uma reta (ponto + vetor) e uma linha vertical.
        """
        if direction_vec.x == 0:
            return Pose2D(vertical_line_x, start_point.y)

        t = int((vertical_line_x - start_point.x) / direction_vec.x)
        intersection_y = start_point.y + t * direction_vec.y

        return Pose2D(vertical_line_x, intersection_y)

    @staticmethod
    def linear_interpolation(start: int, end: int, factor: float) -> int:
        """Interpola linearmente um valor entre um ponto inicial e final."""
        return int(start + (end - start) * factor)
