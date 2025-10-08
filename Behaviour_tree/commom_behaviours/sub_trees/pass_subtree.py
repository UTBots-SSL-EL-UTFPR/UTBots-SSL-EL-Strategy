# pass subtree.py
import py_trees
from Behaviour_tree.core.World_State import TeamID
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.robot.bob import Bob


from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.commom_behaviours import actions as action_nodes
from Behaviour_tree import commom_behaviours as cb

def get_pass_subtree(robot: Bob) -> py_trees.trees.BehaviourTree:
    has_ball = cb.condition.HasBall(robot)
    valid_line= cb.condition.ValidLine(robot)
    receiver_unmarked = cb.condition.ReceiverUnmarked(robot)
    calcular_alinhamento = cb.actions.Calculate_target(robot, name = "Calcular_Alinhamento")
    alinhar = cb.actions.Align(robot, name="Alinhar_Passe")  
    escolhe_passe = cb.actions.Choose_who_to_pass(robot, name="Escolhe_Passe")
    passar = cb.actions.ExecutePass(robot,name="Passar")
    pass_subtree = py_trees.composites.Sequence(
        "passar",
        True,
        children=[has_ball,escolhe_passe,valid_line,receiver_unmarked,calcular_alinhamento,alinhar, passar],
    )

    pass_root = py_trees.trees.BehaviourTree(pass_subtree)
    pass_root.setup()

    return pass_root