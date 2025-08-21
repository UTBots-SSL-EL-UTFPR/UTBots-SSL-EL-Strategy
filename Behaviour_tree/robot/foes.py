from ..core.World_State import World_State, RobotID
from ..core.blackboard import Blackboard_Manager
from utils.pose2D import Pose2D
from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    ATTACK_ZONE,
    MIDFIELD_ZONE,
    DEFENSE_ZONE,
    GOALKEEPER_ZONE,
    BALL_POSSESSION_DISTANCE,
)


class Foes_State:
    #ESTADO SIMPLIFICADO DOS ROBOS INIMIGOS

    def __init__(self, robot_id: RobotID):
        self.blackboard = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.position:Pose2D = Pose2D()
        self.velocity:Pose2D = Pose2D()
        self.has_ball = False
        self.world_state = World_State.get_instance()

    def update(self):
        self.position = self.world_state.get_foe_robot_pose(self.robot_id.value)
        self.velocity = self.world_state.get_foe_robot_velocity(self.robot_id.value)
        self.quadrant_index = self.position.get_quadrant()

    # =================== Métricas / consultas ===================
    def check_ball_possession(self) -> bool:
        ball_position = self.world_state.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE
        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False



    
    