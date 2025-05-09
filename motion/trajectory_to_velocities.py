#Percorre a lista de Pose2D e aplica o MotionMode em pares consecutivos.

from motion.motion_mode import MotionMode
from utils.pose2D import Pose2D
from typing import List, Tuple

class TrajectoryToVelocities:
    def __init__(self, delta_t: float, mode: MotionMode):
        pass

    def compute(self, poses: List[Pose2D]) -> List[Tuple[float, float, float]]:
        pass