from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    ATTACK_QUADRANTS,
    MIDFIELD_QUADRANTS,
    DEFENSE_QUADRANTS,
    GOALKEEPER_ZONE,
    BALL_POSSESSION_DISTANCE,
)

class Pose2D:
    def __init__(self, x=0, y=0, teta=0):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.teta = teta if teta is not None else 0

    #---------------------------------------------------------------------------------------#
    #                                       SOBRECARGAS                                     #
    #---------------------------------------------------------------------------------------#
    
    def __iter__(self): #DESEMPACOTAMENTO 
        yield self.x
        yield self.y
        yield self.teta

    def __repr__(self):
        return f"Point2D(x={self.x}, y={self.y}), "

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
        return self

    def __isub__(self, other):#ponto1 -= ponto2
        if not isinstance(other, Pose2D):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
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
    
    def get_quadrant(self) -> int:
        """Calcula e retorna o índice (1..12) do quadrante atual ou 0 se fora do campo."""
        for i, (x_min, x_max, y_min, y_max) in enumerate(ALL_QUADRANTS, 1):
            if x_min <= self.x <= x_max and y_min <= self.y <= y_max:
                return i
        return 0