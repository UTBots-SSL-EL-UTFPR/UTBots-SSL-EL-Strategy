import math
from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    Zone_Type,
    ATTACK_ZONE,
    MIDFIELD_ZONE,
    DEFENSE_ZONE,
    FOE_GOALKEEPER_ZONE,
    TEAM_GOALKEEPER_ZONE,
    BALL_POSSESSION_DISTANCE,
)

class Pose2D:
    def __init__(self, x=0, y=0, theta=0):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.theta = theta if theta is not None else 0
        self.quadrant = self.get_quadrant()

    #---------------------------------------------------------------------------------------#
    #                                       SOBRECARGAS                                     #
    #---------------------------------------------------------------------------------------#
    def __iter__(self): #DESEMPACOTAMENTO 
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

    def __iadd__(self, other):# Ponto += Ponto
        if not isinstance(other, Pose2D):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        self.quadrant = self.get_quadrant()
        return self

    def __isub__(self, other):#ponto1 -= ponto2
        if not isinstance(other, Pose2D):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        self.quadrant = self.get_quadrant()
        return self
        
    def __eq__(self, other):# ponto1 == ponto2
        if not isinstance(other, Pose2D):
            return False
        return self.x == other.x and self.y == other.y
    
    #---------------------------------------------------------------------------------------#
    #                                   METODOS AUXILIARES                                  #
    #---------------------------------------------------------------------------------------#

    def distance_to(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        from math import sqrt
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def angle_to(self, other):
        if not isinstance(other, Pose2D):
            return NotImplemented
        dx, dy = other.x - self.x, other.y - self.y
        return math.atan2(dy, dx)
    
    @staticmethod
    def align_two(p1: "Pose2D", p2: "Pose2D", margin: int, is_left_team: bool = False) -> "Pose2D":
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
    
    def get_quadrant(self) -> int:
        """Calcula e retorna o índice (1..12) do quadrante atual ou 0 se fora do campo."""
        for i, (x_min, x_max, y_min, y_max) in enumerate(ALL_QUADRANTS, 1):
            if x_min <= self.x <= x_max and y_min <= self.y <= y_max:
                return i
        return 0
    
    def get_zone(self) -> Zone_Type:
        q = self.get_quadrant
        if q in TEAM_GOALKEEPER_ZONE:
            return Zone_Type.TEAM_GOALKEEPER_ZONE
        elif q in MIDFIELD_ZONE:
            return Zone_Type.MIDFIELD_ZONE
        elif q in DEFENSE_ZONE:
            return Zone_Type.DEFENSE_ZONE
        elif q in FOE_GOALKEEPER_ZONE:
            return Zone_Type.FOE_GOALKEEPER_ZONE
        else:
            return Zone_Type.ATTACK_ZONE
        
    def _is_attack_zone(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa ofensiva."""
        return q in ATTACK_ZONE

    def _is_midfield_quadrant(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa de meio-campo."""
        return q in MIDFIELD_ZONE

    def _is_defense_quadrant(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa defensiva."""
        return q in DEFENSE_ZONE

    def _is_in_goalkeeper_zone(self, x: float, y: float) -> bool:
        """Retorna True se (x,y) estiver dentro da zona retangular reservada ao goleiro."""
        xmin, xmax, ymin, ymax = GOALKEEPER_ZONE
        return xmin <= x <= xmax and ymin <= y <= ymax

    def _get_quadrant_type_by_index(self, idx: int):
        """Converte índice num Enum Quadrant_type ou None se inválido."""
        try:
            return Quadrant_type(idx)
        except ValueError:
            return None

    @staticmethod
    def normalize_angle_to_pi(a: float) -> float:
        return (a + math.pi) % (2*math.pi) - math.pi
    
    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        #limita V entre low e high
        return max(lo, min(hi, v))

