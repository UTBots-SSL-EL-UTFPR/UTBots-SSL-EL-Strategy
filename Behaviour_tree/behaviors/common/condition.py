from typing import Any

import py_trees
from py_trees.common import Status

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

ball_flags = BB_flags_and_values.Flags.motion.ball
positions_values = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()
_pos_helper = Positioning_helper.get_object()

# =======================================================================================#
#                                     IMPLEMENTADOS                                     #
# =======================================================================================#


# =======================================================================================#
#                                         x                                             #
# =======================================================================================#


class Has_ball(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Has_ball"):
        super().__init__(name)

    def setup(self, **kwargs: Any) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{ball_flags.has_ball}"):
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.FAILURE

class Valid_Line(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Valid_Line"):
        super().__init__(name)
    
    def setup(self,**kwargs):
        return super().setup(**kwargs)

    def update(self) ->py_trees.common.Status:
        if _bb.get(
          f"{team_flags.Context.valid_line}"
        ):
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.FAILURE


class Receiver_Unmarked(py_trees.behaviour.Behaviour):
    
    def __init__(self, name: str = "Receiver_Unmarked"):
        super().__init__(name)
    
    def setup(self,**kwargs):
        return super().setup(**kwargs)

    def update(self) ->py_trees.common.Status:
        if _bb.get(
          f"{team_flags.Context.unmarked_receiver}"
        ):
            return py_trees.common.Status.RUNNING
        
        return py_trees.common.Status.FAILURE


###class rotation_done(py_trees.behaviour.Behaviour):#rotacionar em relaçaom ao alvo para realizar o passe
#DENTRO DO NO DE AÇAO CHOOSE WHO TO PASS
   ## def __init__(self, Robot:Bob, name: str = "Rotation_done"):
     ##   super().__init__(name)
       # self.robot = Robot
        #self.bb = Blackboard_Manager.get_instance()

    #def update(self) -> py_trees.common.Status:
        #if self.bb.get(
         #   f"{self.robot.robot_id}{positions_values.rotation_done}"
          #  ):
           # return py_trees.common.Status.SUCCESS
     #   return py_trees.common.Status.RUNNING

########PASSE#########################   ACIMAAAAAAAA 


class Ball_visible(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, robot: Bob):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs: Any) -> None:
        if self.robot:
            print("setup")

    def update(self) -> Status:
        if not self.robot or not self.robot.state:
            return py_trees.common.Status.FAILURE

        if _bb.get(f"{self.robot.robot_id.name}{ball_flags.ball_visible}"):
            return py_trees.common.Status.SUCCESS
        key = f"{self.robot.robot_id.name}{positions_values.pos_ball_visible}"
        pos = _bb.get(key)

        if isinstance(pos, Pose2D):
            self.robot.adicionar_ponto_trajetoria(pos)
        else:
            print("blackboard com valor nulo no lugar de pos2d par mov desmarque")
        return py_trees.common.Status.FAILURE

