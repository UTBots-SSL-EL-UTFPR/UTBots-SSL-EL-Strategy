# defines.py - Constantes globais do projeto

from dataclasses import dataclass, field
from enum import Enum
from typing import Set

class RoleType(Enum):
    ATTACK = "attack"
    MIDFIELD = "midfield"
    DEFENSE = "defense"
    GOALKEEPER = "goalkeeper"
    OFFENSIVE_SUPPORT = "offensive_support"
    DEFENSIVE_SUPPORT = "defensive_support"
    KICKER = "Kicker"


# ============================================
# CONSTANTES DO CAMPO SSL
# ============================================
# Dimensões do campo (em milímetros, conforme SSL)
# Em seu arquivo de constantes (defines.py ou similar)

FIELD_WIDTH = 4500
FIELD_HEIGHT = 3000

FIELD_X_MIN = -FIELD_WIDTH / 2  # -2250
FIELD_X_MAX = FIELD_WIDTH / 2   #  2250
FIELD_Y_MIN = -FIELD_HEIGHT / 2  # -1500
FIELD_Y_MAX = FIELD_HEIGHT / 2   #  1500
# Robôs e bola
BOB_RADIUS = 0.09  # Raio do robô Bob em metros
BALL_RADIUS = 0.021  # Raio da bola em metros
BALL_POSSESSION_DISTANCE = BOB_RADIUS + BALL_RADIUS + 0.01  # Distância de posse da bola

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
# Definições dos quadrantes

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



# Passo 1: Criar uma classe para representar uma Zona
@dataclass(frozen=True)
class Zone:
    name: str
    quadrants: Set[Quadrant] = field(default_factory=set)

    def contains(self, x: float, y: float) -> bool:
        """Verifica se um ponto (x, y) está em qualquer um dos quadrantes desta zona."""
        return any(quad.contains(x, y) for quad in self.quadrants)


class ZoneType(Enum):
    ATTACK = Zone("ATTACK", {
        QuadrantType.Q3.value, QuadrantType.Q4.value, QuadrantType.Q7.value, QuadrantType.Q8.value, QuadrantType.Q11.value, QuadrantType.Q12.value
    })
    MIDFIELD = Zone("MIDFIELD", {
        QuadrantType.Q6.value, QuadrantType.Q7.value
    })
    DEFENSE = Zone("DEFENSE", {
        QuadrantType.Q1.value, QuadrantType.Q2.value, QuadrantType.Q5.value, QuadrantType.Q6.value,QuadrantType.Q9.value, QuadrantType.Q10.value
    })

    TEAM_GOALKEEPER = Zone("TEAM_GOALKEEPER", {
        Quadrant("Team GK Area", x_min=-2250, x_max=-1650, y_min=-600, y_max=600)
    })
    FOE_GOALKEEPER = Zone("FOE_GOALKEEPER", {
        Quadrant("Foe GK Area", x_min=1650, x_max=2250, y_min=-600, y_max=600)
    })