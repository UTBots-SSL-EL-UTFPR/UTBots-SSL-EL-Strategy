import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Set

from .defines import FIELD_INVERTED_SIDE

_QUADRANT_INVERT_MAP = {
    "Q1": "Q4",
    "Q2": "Q3",
    "Q3": "Q2",
    "Q4": "Q1",
    "Q5": "Q8",
    "Q6": "Q7",
    "Q7": "Q6",
    "Q8": "Q5",
    "Q9": "Q12",
    "Q10": "Q11",
    "Q11": "Q10",
    "Q12": "Q9",
}


def get_quadrant_type(idx_or_name):
    """
    Retorna o QuadrantType correto considerando o lado do campo.
    Aceita índice (1..12) ou nome ('Q1'..'Q12').
    """
    if isinstance(idx_or_name, int):
        name = f"Q{idx_or_name}"
    else:
        name = str(idx_or_name)
    if FIELD_INVERTED_SIDE:
        name = _QUADRANT_INVERT_MAP.get(name, name)
    return QuadrantType[name]


def get_zone_type(name: str):
    """
    Retorna a Zone_condition_nodes.Valid_Line(),Type correta considerando o lado do campo.
    Para zonas de ataque/defesa, inverte se necessário.
    """
    if FIELD_INVERTED_SIDE:
        if name.upper() == "ATTACK":
            return ZoneType.DEFENSE
        if name.upper() == "DEFENSE":
            return ZoneType.ATTACK
        if name.upper() == "TEAM_GOALKEEPER":
            return ZoneType.FOE_GOALKEEPER
        if name.upper() == "FOE_GOALKEEPER":
            return ZoneType.TEAM_GOALKEEPER
    return ZoneType[name.upper()]


# +------------------------------------------------------------------------+ #
# |                                 RoleType                               | #
# +------------------------------------------------------------------------+ #
class RoleType(Enum):
    ATTACK = "attack"
    MIDFIELD = "midfield"
    DEFENSE = "defense"
    GOALKEEPER = "goalkeeper"
    OFFENSIVE_SUPPORT = "offensive_support"
    DEFENSIVE_SUPPORT = "defensive_support"
    KICKER = "Kicker"


# ============================================
# QUADRANTES DO CAMPO
# Campo SSL dividido em 12 quadrantes (4 horizontais x 3 verticais)
# Coordenadas: X vai de -6000 a +6000, Y vai de -4500 a +4500

#   -2250    -1125       0       1125     2250
#      |        |        |        |        |
# +1500+--------+--------+--------+--------+ +1500
#      |   Q1   |   Q2   |   Q3   |   Q4   |
#  +500+--------+--------+--------+--------+ +500
#      |   Q5   |   Q6   |   Q7   |   Q8   |
#  -500+--------+--------+--------+--------+ -500
#      |   Q9   |   Q10  |   Q11  |   Q12  |
# -1500+--------+--------+--------+--------+ -1500
#      |        |        |        |        |
#   -2250    -1125       0       1125     2250
#

# +------------------------------------------------------------------------+ #
# |                                 Quadrant                               | #
# +------------------------------------------------------------------------+ #


@dataclass(frozen=True)
class Quadrant:
    name: str
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    def contains(self, x: float, y: float) -> bool:
        return (self.x_min <= x < self.x_max) and (self.y_min <= y < self.y_max)

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)


_X_BOUNDS = [-2250, -1125, 0, 1125, 2250]
_Y_BOUNDS = [-1500, -500, 500, 1500]

# +------------------------------------------------------------------------+ #
# |                             QuadrantType                               | #
# +------------------------------------------------------------------------+ #


class QuadrantType(Enum):
    # Superior
    Q1 = Quadrant("Q1", _X_BOUNDS[0], _X_BOUNDS[1], _Y_BOUNDS[2], _Y_BOUNDS[3])
    Q2 = Quadrant("Q2", _X_BOUNDS[1], _X_BOUNDS[2], _Y_BOUNDS[2], _Y_BOUNDS[3])
    Q3 = Quadrant("Q3", _X_BOUNDS[2], _X_BOUNDS[3], _Y_BOUNDS[2], _Y_BOUNDS[3])
    Q4 = Quadrant("Q4", _X_BOUNDS[3], _X_BOUNDS[4], _Y_BOUNDS[2], _Y_BOUNDS[3])
    # Meio
    Q5 = Quadrant("Q5", _X_BOUNDS[0], _X_BOUNDS[1], _Y_BOUNDS[1], _Y_BOUNDS[2])
    Q6 = Quadrant("Q6", _X_BOUNDS[1], _X_BOUNDS[2], _Y_BOUNDS[1], _Y_BOUNDS[2])
    Q7 = Quadrant("Q7", _X_BOUNDS[2], _X_BOUNDS[3], _Y_BOUNDS[1], _Y_BOUNDS[2])
    Q8 = Quadrant("Q8", _X_BOUNDS[3], _X_BOUNDS[4], _Y_BOUNDS[1], _Y_BOUNDS[2])
    # Inferior
    Q9 = Quadrant("Q9", _X_BOUNDS[0], _X_BOUNDS[1], _Y_BOUNDS[0], _Y_BOUNDS[1])
    Q10 = Quadrant("Q10", _X_BOUNDS[1], _X_BOUNDS[2], _Y_BOUNDS[0], _Y_BOUNDS[1])
    Q11 = Quadrant("Q11", _X_BOUNDS[2], _X_BOUNDS[3], _Y_BOUNDS[0], _Y_BOUNDS[1])
    Q12 = Quadrant("Q12", _X_BOUNDS[3], _X_BOUNDS[4], _Y_BOUNDS[0], _Y_BOUNDS[1])


@dataclass(frozen=True)
class Zone:
    name: str
    quadrants: Set[Quadrant] = field(default_factory=set)

    def contains(self, x: float, y: float) -> bool:
        """Verifica se um ponto (x, y) está em qualquer um dos quadrantes desta zona."""
        return any(quad.contains(x, y) for quad in self.quadrants)


# +------------------------------------------------------------------------+ #
# |                              ZoneType                                  | #
# +------------------------------------------------------------------------+ #


class ZoneType(Enum):
    ATTACK = Zone(
        "ATTACK",
        {
            QuadrantType.Q3.value,
            QuadrantType.Q4.value,
            QuadrantType.Q7.value,
            QuadrantType.Q8.value,
            QuadrantType.Q11.value,
            QuadrantType.Q12.value,
        },
    )
    MIDFIELD = Zone("MIDFIELD", {QuadrantType.Q6.value, QuadrantType.Q7.value})
    DEFENSE = Zone(
        "DEFENSE",
        {
            QuadrantType.Q1.value,
            QuadrantType.Q2.value,
            QuadrantType.Q5.value,
            QuadrantType.Q6.value,
            QuadrantType.Q9.value,
            QuadrantType.Q10.value,
        },
    )

    TEAM_GOALKEEPER = Zone(
        "TEAM_GOALKEEPER",
        {Quadrant("Team GK Area", x_min=-2250, x_max=-1650, y_min=-600, y_max=600)},
    )
    FOE_GOALKEEPER = Zone(
        "FOE_GOALKEEPER",
        {Quadrant("Foe GK Area", x_min=1650, x_max=2250, y_min=-600, y_max=600)},
    )


class Pose2D:
    def __init__(self, x=0, y=0, theta=0):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.theta = theta if theta is not None else 0

    # ---------------------------------------------------------------------------------------#
    #                                       SOBRECARGAS                                     #
    # ---------------------------------------------------------------------------------------#
    def __iter__(self):  # DESEMPACOTAMENTO
        yield self.x
        yield self.y
        yield self.theta

    def __repr__(self):
        return f"Point2D(x={self.x}, y={self.y}), theta = {self.theta} "

    def __add__(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        return Pose2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        return Pose2D(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):  # Ponto += Ponto
        if not isinstance(other, Pose2D):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):  # ponto1 -= ponto2
        if not isinstance(other, Pose2D):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self

    def __eq__(self, other):  # ponto1 == ponto2
        if not isinstance(other, Pose2D):
            return False
        return self.x == other.x and self.y == other.y

    # ---------------------------------------------------------------------------------------#
    #                                     PROPRIEDADES                                      #
    # ---------------------------------------------------------------------------------------#

    @property
    def quadrant(self) -> QuadrantType | None:
        for quad_enum in QuadrantType:
            if quad_enum.value.contains(self.x, self.y):
                return quad_enum
        return None

    @property
    def zone(self) -> ZoneType | None:
        for zone_enum in ZoneType:
            if zone_enum.value.contains(self.x, self.y):
                return zone_enum
        return None

    def inside_area(self, x_min, x_max, y_min, y_max) -> bool:
        return (x_min < self.x < x_max) and (y_min < self.y < y_max)

    # ---------------------------------------------------------------------------------------#
    #                                   METODOS AUXILIARES                                  #
    # ---------------------------------------------------------------------------------------#

    def distance_to(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        from math import sqrt

        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def angle_to(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        dx, dy = other.x - self.x, other.y - self.y
        return math.atan2(dy, dx)

    @staticmethod
    def align_two(
        p1: "Pose2D", p2: "Pose2D", margin: int, is_left_team: bool = False
    ) -> "Pose2D":
        """
        Gera um terceiro ponto alinhado com a reta formada por p1->p2,
        deslocando 'atrás' ou 'à frente' da reta por uma margem fixa.

        """
        dx, dy = (p2.x - p1.x), (p2.y - p1.y)
        length = math.hypot(dx, dy)
        if length == 0:
            raise ValueError("p1 e p2 não podem ser iguais")

        # Direção unitária p1->p2
        dir_x, dir_y = dx / length, dy / length

        # Decide sinal de deslocamento (atrás ou à frente)
        sign = -1 if is_left_team else +1

        # Calcula novo ponto partindo de p2
        target_x = p1.x + sign * dir_x * margin
        target_y = p1.y + sign * dir_y * margin

        # Orientação: ângulo da reta p1->p2 em graus inteiros
        theta = int(round(math.degrees(math.atan2(dy, dx))))

        return Pose2D(int(round(target_x)), int(round(target_y)), theta)

    def is_in_range(self, other, threshould):
        return self.distance_to(other) < threshould

    @staticmethod
    def normalize_angle_to_pi(a: float) -> float:
        return (a + math.pi) % (2 * math.pi) - math.pi

    @staticmethod
    def _clamp(v: int, lo: int, hi: int) -> int:
        # limita V entre low e high
        return max(lo, min(hi, v))

    def distance_to_sq(self, other: "Pose2D") -> float:
        """
        Calcula a distância euclidiana AO QUADRADO para outro ponto.
        É mais rápido que distance_to() pois evita a raiz quadrada.
        """
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
