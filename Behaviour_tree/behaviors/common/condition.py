import py_trees
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BB_flags_and_values

ball_flags = BB_flags_and_values.Flags.motion.ball
positions_values = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags
_bb = Blackboard_Manager.get_instance()

#=======================================================================================#
#                                     IMPLEMENTADOS                                     #
#=======================================================================================#





#=======================================================================================#
#                                         x                                             #
#=======================================================================================#

class Has_ball(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Has_ball"):
        super().__init__(name)
        

    def update(self) -> py_trees.common.Status:
        if _bb.get(
            f"{ball_flags.has_ball}"
        ):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE