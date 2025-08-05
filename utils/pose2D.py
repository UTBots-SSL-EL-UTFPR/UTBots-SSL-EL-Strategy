class Pose2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.theta = theta
        
    def distance_to(self, other):
        from math import sqrt
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
