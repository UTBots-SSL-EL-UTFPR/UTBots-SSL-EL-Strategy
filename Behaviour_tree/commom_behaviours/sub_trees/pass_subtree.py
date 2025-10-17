# pass subtree.py
import py_trees

from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.commom_behaviours import actions as action_nodes
from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.core.World_State import TeamID
from Behaviour_tree.robot.bob import Bob


def get_pass_subtree(robot: Bob) -> py_trees.behaviour.Behaviour:
    has_ball = cb.condition.HasBall(robot)
    valid_line = cb.condition.ValidLine(robot)
    receiver_unmarked = cb.condition.ReceiverUnmarked(robot)
    calculate_angular_position = cb.actions.Calculate_angular_target_pass(robot)
    calculate_linear_position = cb.actions.Calculate_linear_target_pass(robot)
    alinhamento_angular = cb.actions.Angular_align_pass(robot)
    alinhamento_linear = cb.actions.Move_node(robot)
    escolhe_passe = cb.actions.Choose_who_to_pass(robot, name="Escolhe_Passe")
    passar = cb.actions.ExecutePass(robot, name="Passar")
    pass_subtree = py_trees.composites.Sequence(
        "passar",
        True,
        children=[
            has_ball,
            escolhe_passe,
            valid_line,
            receiver_unmarked,
            calculate_angular_position,
            calculate_linear_position,
            alinhamento_angular,
            alinhamento_linear,
            passar,
        ],
    )

    # pass_root = py_trees.trees.BehaviourTree(pass_subtree)
    # pass_root.setup()
    pass_subtree.setup()
    return pass_subtree
