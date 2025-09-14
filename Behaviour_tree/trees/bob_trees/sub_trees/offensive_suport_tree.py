from Behaviour_tree.behaviors.common import actions, condition
from typing import Callable, Tuple, Optional
from utils.pose2D import Pose2D
import py_trees
from Behaviour_tree.robot.bob import Bob
import py_trees
from typing import Callable, Tuple, Optional
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import RobotID


#----------------------------------------------------------------------------------------------------------------------#

robot = Bob(RobotID.Defender)
suport_repos = py_trees.composites.Selector("posicionamento receber passe ou rebote", False, 
                                            children=[])

brigar_pela_bola = py_trees.composites.Sequence("suporte briga pela bola", True,
                                                children=[suport_repos, actions.Move_node("Move_suport_repos", robot), ])


