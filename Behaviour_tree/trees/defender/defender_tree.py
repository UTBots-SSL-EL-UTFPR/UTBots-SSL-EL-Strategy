# Behaviour_tree/trees/defender/defender_tree.py
import py_trees
import time
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree import commom_behaviours as cb
from utils.pose2D import Pose2D

from .defender_conditions import IsBallAThreat, IsOpponentWithBallInDangerZone, IsBallInDefensiveHalf
from .defender_strategy_helper import DefenderStrategyHelper

class DefenderStrategicMove(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str, delta_t: float = 1.0):
        super().__init__(name)
        self.robot = robot
        self.delta_t = delta_t
        self.last_path: list[Pose2D] = []
        self._last_update_time = 0.0

    def initialise(self):
        self._recalculate_path()

    def update(self):
        current_time = time.time()
        if (current_time - self._last_update_time) > self.delta_t:
            self._recalculate_path()
        if self.last_path: self.robot.set_path(self.last_path)
        return py_trees.common.Status.SUCCESS

    def _recalculate_path(self):
        raise NotImplementedError

class Intercept(DefenderStrategicMove):
    def __init__(self, robot: Bob, name: str = "Definir Alvo de Interceptação"):
        super().__init__(robot=robot, name=name, delta_t=0.5)
    def _recalculate_path(self):
        self.robot.state.current_command = "Interceptando Ameaça!"
        target = DefenderStrategyHelper.get_intercept_position(self.robot.state.position)
        if target: self.last_path = DefenderStrategyHelper.get_path_to_target(self.robot.state.position, target)
        self._last_update_time = time.time()

class PositionDefensively(DefenderStrategicMove):
    def __init__(self, robot: Bob, name: str = "Posicionar Defensivamente"):
        super().__init__(robot=robot, name=name, delta_t=1.0)
    def _recalculate_path(self):
        self.robot.state.current_command = "Posicionando Defensivamente"
        target = DefenderStrategyHelper.get_smart_defensive_position()
        if target: self.last_path = DefenderStrategyHelper.get_path_to_target(self.robot.state.position, target)
        self._last_update_time = time.time()

class ReturnToBase(DefenderStrategicMove):
    def __init__(self, robot: Bob, name: str = "Definir Alvo Base"):
        super().__init__(robot=robot, name=name, delta_t=2.0)
    def _recalculate_path(self):
        self.robot.state.current_command = "Retornando para a Base"
        target = DefenderStrategyHelper.get_base_position()
        self.last_path = DefenderStrategyHelper.get_path_to_target(self.robot.state.position, target)
        self._last_update_time = time.time()

def get_defender_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    # A árvore precisa de todos os ramos para tomar a decisão correta
    intercept_branch = py_trees.composites.Sequence("Ramo: Interceptar", memory=True, children=[IsBallAThreat(), Intercept(robot), cb.actions.Move_node(robot)])
    block_branch = py_trees.composites.Sequence("Ramo: Bloquear", memory=True, children=[IsOpponentWithBallInDangerZone(), PositionDefensively(robot), cb.actions.Move_node(robot)])
    cover_branch = py_trees.composites.Sequence("Ramo: Cobrir", memory=True, children=[IsBallInDefensiveHalf(), PositionDefensively(robot), cb.actions.Move_node(robot)])
    base_branch = py_trees.composites.Sequence("Ramo: Base", memory=True, children=[ReturnToBase(robot), cb.actions.Move_node(robot)])

    # A raiz reativa (memory=False) garante que o robô sempre reavalie as prioridades
    root = py_trees.composites.Selector(
        "Comportamento do Defensor", memory=False, 
        children=[intercept_branch, block_branch, cover_branch, base_branch]
    )
    return py_trees.trees.BehaviourTree(root)