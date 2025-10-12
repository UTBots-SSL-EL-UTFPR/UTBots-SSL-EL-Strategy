# teste passe

import time

import py_trees as pt

from Behaviour_tree.managers.bob_manager import BobManager
from Behaviour_tree.commom_behaviours import actions as s_action_nodes
from Behaviour_tree.commom_behaviours import condition as c_condition_nodes
from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID, World_State
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

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

    # @DANILO - voce precisa instanciar as classes antes de colocar em children
    # segue um exemplo
    # has_ball = c_condition_nodes.HasBall(passer)

    pass_sequence = pt.composites.Sequence(
        name="Pass Tactic",
        memory=True,
        children=[
            c_condition_nodes.Has_ball(robot=passer),
            c_condition_nodes.Valid_Line(),
            c_condition_nodes.Receiver_Unmarked(robot=receiver),
            s_action_nodes.Choose_who_to_pass(robot=passer, name="Choose Receiver"),
            s_action_nodes.Set_blackboard_value(
                "pass_executed", True, name="Execute Pass (Placeholder)"
            ),
        ],
    )

    # @DANILO acho q eu ja fiz a arvore do recebedor nos suportes
    # FALTA A ARVORE DO RECEBEDOR E TERMINAR DE MONTAR AS ARVORES E a main para testar
