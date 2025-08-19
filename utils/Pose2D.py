
class Pose2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    #---------------------------------------------------------------------------------------#
    #                                       SOBRECARGAS                                     #
    #---------------------------------------------------------------------------------------#

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

    def distance_to(self, other):
        from math import sqrt
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)