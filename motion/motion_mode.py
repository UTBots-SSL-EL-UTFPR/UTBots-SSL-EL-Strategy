#classe base abstrata
from abc import ABC, abstractmethod
from typing import Tuple
from utils.pose2D import Pose2D


class MotionMode(ABC):
    @abstractmethod
    def calculate(self, pose1: Pose2D, pose2:Pose2D, delta_t: float) -> Tuple[float, float, float]:
        pass
    