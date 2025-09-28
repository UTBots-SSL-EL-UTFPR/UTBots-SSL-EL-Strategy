# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #

from dataclasses import dataclass, field
from enum import Enum
from typing import Set

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


# Flag global: True se o time defende o gol da direita (campo invertido)
FIELD_INVERTED_SIDE = False  # Altere para True se seu time defende o lado direito

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


# +------------------------------------------------------------------------+ #
# |                             FieldHelper                                | #
# +------------------------------------------------------------------------+ #


class FieldHelper:

    @classmethod
    def get_goal_center(cls) -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= config.get_side_sign()
        return goal_pose
