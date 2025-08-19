from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    Zone_Type,
    ATTACK_ZONE,
    MIDFIELD_ZONE,
    DEFENSE_ZONE,
    GOALKEEPER_ZONE,
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
        from math import sqrt
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        
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
        if q in ATTACK_ZONE:
            return Zone_Type.ATTACK_ZONE
        elif q in MIDFIELD_ZONE:
            return Zone_Type.MIDFIELD_ZONE
        elif q in DEFENSE_ZONE:
            return Zone_Type.DEFENSE_ZONE
        else:
            return Zone_Type.GOALKEEPER_ZONE
        
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