#Percorre a lista de Pose2D e aplica o MotionMode em pares consecutivos.

from motion.motion_mode import MotionMode
from utils.pose2D import Pose2D
from typing import List, Tuple

class TrajectoryToVelocities:
    def __init__(self, delta_t: float, mode: MotionMode): #mode é uma instancia de MotionMode
        self.delta_t = delta_t
        self.mode = mode

    def convert(self, poses: List[Pose2D]) -> List[Tuple[float, float, float]]:
        #chamar a calculate correta dependendo do MotionMode para transformar as poses2d em vx, vy e w
        
        velocities = []

        for i in range(len(poses) - 1):
            pose1 = poses[i]
            pose2 = poses[i + 1]
            vx, vy, omega = self.mode.calculate(pose1, pose2, self.delta_t)
            velocities.append((vx, vy, omega))
        return velocities