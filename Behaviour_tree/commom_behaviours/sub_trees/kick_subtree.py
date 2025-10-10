# kick subtree.py
import py_trees

from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.commom_behaviours import actions as action_nodes
from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.core.World_State import TeamID
from Behaviour_tree.robot.bob import Bob


def get_kick_subtree(robot: Bob) -> py_trees.trees.BehaviourTree:
    # posse_aliada = cb.condition.HasBall(robot)
    visibilidade_gol = cb.condition.Goal_visibility(attacker=robot, name="Ve o gol")
    distancia_gol = cb.condition.Goal_distance(attacker=robot, name="Ve o gol")

    calcular_target_position = cb.actions.Calculate_kick_target(robot)
    alinhar_com_gol = cb.actions.Align(robot)
    chutar_gol = cb.actions.Shoot_to_goal(robot)
    kick_subtree = py_trees.composites.Sequence(
        "chutar no gol",
        True,
        children=[visibilidade_gol, distancia_gol, alinhar_com_gol, chutar_gol],
    )

    kick_root = py_trees.trees.BehaviourTree(kick_subtree)
    kick_root.setup()

    return kick_root
