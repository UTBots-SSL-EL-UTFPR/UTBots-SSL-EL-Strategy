#classe derivada de MotionMode. Vai calcular (vx, vy, ω) entre dois poses com orientação

from motion.motion_mode import MotionMode
from utils.pose2D import Pose2D
from typing import Tuple

class WithBallMotionMode(MotionMode):
    def calculate(self, pose1: Pose2D, pose2: Pose2D, delta_t: float) -> Tuple[float, float, float]:
        pass
        