from enum import Enum

from utils.defines import BALL_POSSESSION_DISTANCE
from utils.pose2D import Pose2D

from ..core import event_callbacks
from ..core.blackboard import Blackboard_Manager
from ..core.World_State import TeamID, World_State


class FoesState:
    # ESTADO SIMPLIFICADO DOS ROBOS INIMIGOS

    def __init__(self, robot_id: TeamID):
        self.blackboard = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.position: Pose2D = Pose2D()
        self.has_ball = False
        self.robot_id = id

    def update(self):
        if position := self._ws.get_foe_robot_pose(self.robot_id.value):
            self.position = position
        self.is_ball_with_robot()

    # =================== Métricas / consultas ===================
    def check_ball_possession(self) -> bool:
        ball_position = self._ws.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE

        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False

    def is_ball_with_robot(self):
        if self.has_ball != self.check_ball_possession():
            if self.has_ball:
                event_callbacks.foes_lost_ball_posetion(self.robot_id.name)
            else:
                self.ball_visible = True
                event_callbacks.foes_got_ball_posetion(self.robot_id.name)
            self.has_ball = not self.has_ball
