from enum import Enum

from utils.defines import BALL_POSSESSION_DISTANCE
from utils.pose2D import Pose2D

from ..core import event_callbacks
from ..core.blackboard import Blackboard_Manager
from ..core.World_State import World_State


class FoesID(Enum):
    TauraBots = 0
    GralhaBots = 1
    Cerberus = 2


class FoeState:
    """ESTADO SIMPLIFICADO DOS ROBOS INIMIGOS"""

    def __init__(self, id: FoesID):
        self.has_ball = False
        self.robot_id = id

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Pose2D | None):
        if value is not None:
            self._position = value

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value: Pose2D | None):
        if value is not None:
            self._velocity = value
