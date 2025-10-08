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

    @staticmethod
    def project_point_on_line(
        point: Pose2D, line_origin: Pose2D, line_direction: Pose2D
    ) -> Pose2D:
        """
        Projeta um ponto em uma linha definida por uma origem e um vetor de direção.
        """
        # Vetor da origem da linha até o ponto a ser projetado
        vec_to_point_x = point.x - line_origin.x
        vec_to_point_y = point.y - line_origin.y

        # Vetor de direção da linha (não precisa ser unitário)
        dir_x = line_direction.x
        dir_y = line_direction.y
        
        dir_mag_sq = dir_x**2 + dir_y**2
        if dir_mag_sq < 1e-6: # Evita divisão por zero se a direção for nula
            return line_origin

        # O produto escalar nos dá o "quanto" do vec_to_point está na direção da linha
        dot_product = vec_to_point_x * dir_x + vec_to_point_y * dir_y
        
        # t é o fator de escala ao longo do vetor de direção
        t = dot_product / dir_mag_sq
        
        # Garante que a projeção seja para frente na trajetória da bola
        t = max(0, t)

        # Calcula as coordenadas do ponto projetado
        projected_x = line_origin.x + t * dir_x
        projected_y = line_origin.y + t * dir_y

        return Pose2D(projected_x, projected_y)