#strategy/conditions
import py_trees
from ...robot.bob import Bob
from ...core.World_State import RobotID
from ...core.blackboard import Blackboard_Manager
from ...core.event_callbacks import BB_flags_and_values

ball_flags = BB_flags_and_values.Flags.motion.ball
positions_values = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()
#=======================================================================================#
#                                     IMPLEMENTADOS                                     #
#=======================================================================================#


#---------------------------------------------------------------------------------------#
#                                     CONTEXTOS                                         #
#---------------------------------------------------------------------------------------#

#=========================================ATTACK========================================#
class is_atack_from_recovery(py_trees.behaviour.Behaviour): #exemplo
    def __init__(self, name: str="verify atack from recovery"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.SUCCESS

class is_slow_attack(py_trees.behaviour.Behaviour): 
    def __init__(self, name: str="verify is_slow_attack"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.FAILURE

class Pass(py_trees.behavior.Behaviour):
    def __init__(self,name:str="verify_pass"):
        super().__init__(name)
        

    def update(self) -> py_trees.common.Status:
        

        return py_trees.common.Status.FAILURE
    

class is_simple_atack(py_trees.behaviour.Behaviour):
    def __init__(self, name: str="verify simple atack"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        for robot_id in RobotID:
            pos = _bb.get(f"{robot_id}{positions_values.quadrant}")
            if (pos is not None) and (pos > 6):
                return py_trees.common.Status.FAILURE
        return py_trees.common.Status.FAILURE
#========================================Defense========================================#
class exemple_of_defense(py_trees.behaviour.Behaviour): #exemplo #TODO
    def __init__(self, name: str="verify exemple_of_defense"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.FAILURE


#---------------------------------------------------------------------------------------#
#                                    POSSE_BOLA                                         #
#---------------------------------------------------------------------------------------#
class Team_Has_ball_posetion(py_trees.behaviour.Behaviour): #TODO se o will conseguir fazer uma unica variavel que verifica se o time tem posse, e muda caso um dos robos encontre a bola...

    def __init__(self, name: str = "verify team ball posetion"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
            for robot_id in RobotID:
                posetion = _bb.get(f"{robot_id}{ball_flags.has_ball}")
                if posetion:
                    return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.FAILURE

    
class Foes_Have_ball_posetion(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "verify foes have ball posetion"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        if _bb.get(
            f"{ball_flags.has_ball}"
        ):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
    
#---------------------------------------------------------------------------------------#
#                                    POSICIONAMENTO                                     #
#---------------------------------------------------------------------------------------#
class is_in_left_side(py_trees.behaviour.Behaviour):
    """
    temos que definir como vamos tratar o lado adversario etc.., aqui assumi mais q 6
    """
    def __init__(self, robot: Bob, name: str = "verify left side"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        pos = _bb.get(
            f"{self.robot.robot_id}{positions_values.quadrant}"
        ) 
        if (pos is not None ) and (pos > 6):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE