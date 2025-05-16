#classe derivada de MotionMode. Vai calcular (vx, vy, 0) — ignora orientação.

from motion.motion_mode import MotionMode
from utils.pose2D import Pose2D
from typing import Tuple

class WithoutBallMotionMode(MotionMode):
    def calculate(self, pose1: Pose2D, pose2: Pose2D, delta_t: float) -> Tuple[float, float, float]:
        vx = (pose2.x - pose1.x) / delta_t
        vy = (pose2.y - pose1.y) / delta_t
        omega = 0.0 #velocidade angular do robo nao interessa quando nao temos a posse da bola
        return vx, vy, omega

        