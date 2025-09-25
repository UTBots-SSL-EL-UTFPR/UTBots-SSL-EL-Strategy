#teste passe

from Behaviour_tree.core.World_State import World_State, RobotID
from Behaviour_tree.robot.bob import Bob
import time
import py_trees as pt
from utils.pose2D import Pose2D
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core import event_callbacks as callbacks


from ....behaviors.common import condition as c_condition_nodes
from ....behaviors.strategy import actions as s_action_nodes 

from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.bob_manager import BobManager


TICK_INTERVAL = 0.1 

def main() -> None:
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    

    passer = bob_state.get_bob(RobotID.Kamiji)
    receiver = bob_state.get_bob(RobotID.Defender)
    goalkeeper = bob_state.get_bob(RobotID.Goalkeeper)

    if passer is None or receiver is None or goalkeeper is None: 
        print("Erro: Robôs não encontrados.")
        return

    # --- DEFINIÇÃO DAS ÁRVORES DE COMPORTAMENTO ---

    pass_sequence = pt.composites.Sequence(
        name="Pass Tactic",
        memory=True, 
        children=[
            c_condition_nodes.Has_ball(robot=passer),
            c_condition_nodes.Valid_Line(),
            c_condition_nodes.Receiver_Unmarked(robot=receiver),
            s_action_nodes.Choose_who_to_pass(robot=passer, name="Choose Receiver"),
           
            s_action_nodes.Set_blackboard_value("pass_executed", True, name="Execute Pass (Placeholder)")
           
        ]
    )

    #FALTA A ARVORE DO RECEBEDOR E TERMINAR DE MONTAR AS ARVORES E a main para testar