#Converte cada (vx, vy, ω) em velocidades para as 4 rodas.
from typing import List
import math

class InverseKinematics:
    def __init__(self, wheel_angles: List[float], wheel_radius: float, robot_radius: float):
        self.thetas = [math.radians(theta) for theta in wheel_angles]
        self.r = wheel_radius
        self.R = robot_radius

    def compute(self, vx: float, vy: float, omega: float) -> List[float]:
        wheel_speeds = []
        for theta in self.thetas:
            speed = (-math.sin(theta) * vx + math.cos(theta) * vy + self.R * omega) / self.r
            wheel_speeds.append(speed)
        return wheel_speeds
