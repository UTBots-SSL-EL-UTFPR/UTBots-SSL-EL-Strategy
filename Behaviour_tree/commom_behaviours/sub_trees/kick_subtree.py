# kick subtree.py
import py_trees
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.bob_manager import BobManager

from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.commom_behaviours import actions as action_nodes


class KickTree :
    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id
        self.bob_manager = BobManager.get_object()
        self.robot = self.bob_manager.get_bob(self.robot_id)
        
        if self.robot is None:
            raise ValueError(f"Robô com ID {robot_id} não encontrado.")


    def create_tree(self) -> py_trees.behaviour.Behaviour:
        if not self.robot:
            return py_trees.behaviours.Failure("Robô não inicializado")

    # CONDIÇÕES
        has_ball = condition_nodes.HasBall(robot=self.robot, name="Tem a bola")
        goal_visibility = condition_nodes.Goal_visibility(attacker=self.robot, name="Ve o gol")
        goal_distance = condition_nodes.Goal_distance(attacker=self.robot, name="Distancia Valida")
        kick_conditions = py_trees.composites.Sequence(
            "Condicoes de chute",
             memory=True,
             children=[
                 has_ball,
                 goal_visibility,
                 goal_distance
                 ]
        )

    # AÇÕES
        align_for_shoot = action_nodes.Align_for_shoot(attacker=self.robot, name="Alinha com o gol")
        shoot_to_goal = action_nodes.Shoot_to_goal(attacker=self.robot, name="Chuta no gol")
        kick_actions = py_trees.composites.Sequence(
            "Acoes de chute",
            memory=True,
            children=[
                align_for_shoot,
                shoot_to_goal
                ]
        )

    # RAÍZ
        kick_subtree = py_trees.composites.Sequence(
            "arvore de chute",
            memory=True,
            children=[
                kick_conditions,
                kick_actions
                ]
        )
        return kick_subtree
    

