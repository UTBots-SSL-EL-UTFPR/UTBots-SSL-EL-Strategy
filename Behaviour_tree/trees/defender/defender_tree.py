# Behaviour_tree/trees/defender/defender_tree.py
import py_trees
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.core.blackboard import Blackboard_Manager

# Importa as novas condições e estratégias
from .defender_conditions import (
    IsBallMovingFastTowardsGoal,
    IsOpponentWithBallInDangerZone,
    IsBallInDefensiveHalf,
)
from .defender_strategy_helper import DefenderStrategyHelper
_bb = Blackboard_Manager.get_instance()
# --- Comportamentos "Cola" que conectam a estratégia com a ação ---

class Intercept(py_trees.behaviour.Behaviour):
    def __init__(self, path: str, name: str = "Definir Alvo de Interceptação"):
        super().__init__(name)
        self.path = path

    def update(self) -> py_trees.common.Status:
        robot: Bob = _bb.get(self.path)
        target = DefenderStrategyHelper.get_intercept_position()
        if not target: return py_trees.common.Status.FAILURE
        path = DefenderStrategyHelper.get_path_to_target(robot.state.position, target)
        robot.set_path(path)
        robot.state.current_command = "Interceptando Ameaça!"
        return py_trees.common.Status.SUCCESS

class BlockOpponent(py_trees.behaviour.Behaviour):
    def __init__(self, path: str, name: str = "Definir Alvo de Bloqueio"):
        super().__init__(name)
        self.path = path

    def update(self) -> py_trees.common.Status:
        robot: Bob = _bb.get(self.path)
        target = DefenderStrategyHelper.get_blocking_position()
        path = DefenderStrategyHelper.get_path_to_target(robot.state.position, target)
        robot.set_path(path)
        robot.state.current_command = "Bloqueando Oponente"
        return py_trees.common.Status.SUCCESS

class CoverZone(py_trees.behaviour.Behaviour):
    def __init__(self, path: str, name: str = "Definir Alvo de Cobertura"):
        super().__init__(name)
        self.path = path

    def update(self) -> py_trees.common.Status:
        robot: Bob = _bb.get(self.path)
        target = DefenderStrategyHelper.get_zonal_marking_position()
        path = DefenderStrategyHelper.get_path_to_target(robot.state.position, target)
        robot.set_path(path)
        robot.state.current_command = "Cobindo Zona Defensiva"
        return py_trees.common.Status.SUCCESS

class ReturnToBase(py_trees.behaviour.Behaviour):
    def __init__(self, path: str, name: str = "Definir Alvo Base"):
        super().__init__(name)
        self.path = path

    def update(self) -> py_trees.common.Status:
        robot: Bob = _bb.get(self.path)
        target = DefenderStrategyHelper.get_base_position()
        path = DefenderStrategyHelper.get_path_to_target(robot.state.position, target)
        robot.set_path(path)
        robot.state.current_command = "Retornando para a Base"
        return py_trees.common.Status.SUCCESS

# --- Função Principal que Monta a Árvore ---

def get_defender_tree(path: str) -> py_trees.trees.BehaviourTree:
    """Monta a árvore de comportamento completa para o papel de Defensor."""
    
    # Ramo 1: Interceptar (Prioridade Máxima)
    intercept_branch = py_trees.composites.Sequence(
        "Ramo: Interceptar", memory=True,
        children=[
            IsBallMovingFastTowardsGoal(), 
            Intercept(path), 
            cb.actions.Move_node(path, name="Executar Movimento") # CORREÇÃO: Nova instância
        ]
    )

    # Ramo 2: Bloquear Oponente
    block_branch = py_trees.composites.Sequence(
        "Ramo: Bloquear", memory=True,
        children=[
            IsOpponentWithBallInDangerZone(), 
            BlockOpponent(path), 
            cb.actions.Move_node(path, name="Executar Movimento") # CORREÇÃO: Nova instância
        ]
    )
    
    # Ramo 3: Cobrir Zona
    cover_branch = py_trees.composites.Sequence(
        "Ramo: Cobrir", memory=True,
        children=[
            IsBallInDefensiveHalf(), 
            CoverZone(path), 
            cb.actions.Move_node(path, name="Executar Movimento") # CORREÇÃO: Nova instância
        ]
    )
    
    # Ramo 4: Voltar para a Base (Fallback)
    base_branch = py_trees.composites.Sequence(
        "Ramo: Base", memory=True,
        children=[
            ReturnToBase(path), 
            cb.actions.Move_node(path, name="Executar Movimento") # CORREÇÃO: Nova instância
        ]
    )

    # Raiz: Selector que define as prioridades
    root = py_trees.composites.Selector(
        "Comportamento do Defensor", memory=True,
        children=[intercept_branch, block_branch, cover_branch, base_branch]
    )

    return py_trees.trees.BehaviourTree(root)