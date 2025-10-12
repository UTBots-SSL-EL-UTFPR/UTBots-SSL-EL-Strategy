# kick subtree.py
import py_trees
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.robot.bob import Bob


from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.commom_behaviours import actions as action_nodes
from Behaviour_tree import commom_behaviours as cb

def get_kick_subtree(robot: Bob) -> py_trees.trees.BehaviourTree:
    posse_da_bola = cb.condition.HasBall(robot)
    is_in_goalkeeper_area = cb.condition.Is_in_prohibited_area(robot)
    visibilidade_gol = cb.condition.Goal_visibility(robot)
    ball_safety = cb.condition.BolaSegura(robot)
    distancia_gol = cb.condition.Goal_distance(robot)

    calculate_angular_position = cb.actions.Calculate_angular_target(robot)
    calculate_linear_position = cb.actions.Calculate_linear_target(robot)
    alinhamento_angular = cb.actions.Angular_align(robot)
    alinhamento_linear = cb.actions.Move_node(robot)
    chutar_gol = cb.actions.Shoot_to_goal(robot)
    kick_subtree = py_trees.composites.Sequence(
        "chutar no gol",
        True,
        children=[posse_da_bola, is_in_goalkeeper_area, ball_safety, visibilidade_gol, distancia_gol, calculate_linear_position, alinhamento_linear, calculate_angular_position, alinhamento_angular, chutar_gol]
    )

    kick_root = py_trees.trees.BehaviourTree(kick_subtree)
    kick_root.setup()

    return kick_root


