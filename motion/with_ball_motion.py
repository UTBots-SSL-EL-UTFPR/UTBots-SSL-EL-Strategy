#classe derivada de MotionMode. Vai calcular (vx, vy, ω) entre dois poses com orientação
import math
from motion.motion_mode import MotionMode
from utils.pose2D import Pose2D
from typing import Tuple

class WithBallMotionMode(MotionMode):
    def calculate(self, pose1: Pose2D, pose2: Pose2D, delta_t: float) -> Tuple[float, float, float]:
        vx = (pose2.x - pose1.x) / delta_t
        vy = (pose2.y - pose1.y) / delta_t

        #aqui a gente calcula a menor diferença angular no intervalo [-π, π]
        dtheta = (pose2.theta - pose1.theta + math.pi) % (2 * math.pi) - math.pi
        omega = dtheta / delta_t #velocidade angular aqui é em rad/s

        return vx, vy, omega
    
    def requires_orientation(self) -> bool:
        return True

        