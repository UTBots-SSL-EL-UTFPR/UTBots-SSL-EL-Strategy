import logging
import py_trees

# ===================================================================================== #
# IMPORTAÇÕES DO SEU PROJETO
# ===================================================================================== #

from .defender_actions import DefenderActions
from .defender_conditions import (
    Ball_in_defensive_area,
    Ball_moving_towards_goal,
    Opponent_has_ball_in_danger_zone,
)
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree.core.blackboard import Blackboard_Manager
from utils.pose2D import Pose2D

logger = logging.getLogger(__name__)

# ===================================================================================== #
# ADAPTADORES DE AÇÃO (Wrappers)
# ===================================================================================== #

class CalculateDefensivePosition(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Calcular Posição de Defesa"):
        super().__init__(name)
        self.robot = robot
        self.actions_logic = DefenderActions(name="DefenderActionsLogic", blackboard=Blackboard_Manager.get_instance())

    def update(self) -> py_trees.common.Status:
        target_pose = self.actions_logic.set_defensive_position(self.robot.robot_id)
        if target_pose:
            self.robot.set_new_target(target_pose)
            self.robot.state.current_command = "Posicionar para bloquear"
            logger.debug(f"{self.name}: Novo alvo defensivo definido em {target_pose}")
            return py_trees.common.Status.SUCCESS
        logger.warning(f"{self.name}: Não foi possível calcular a posição defensiva.")
        return py_trees.common.Status.FAILURE

class CalculateInterceptPosition(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Calcular Ponto de Interceptação"):
        super().__init__(name)
        self.robot = robot
        self.actions_logic = DefenderActions(name="DefenderActionsLogic", blackboard=Blackboard_Manager.get_instance())

    def update(self) -> py_trees.common.Status:
        target_pose = self.actions_logic.intercept_ball(self.robot.robot_id)
        if target_pose:
            self.robot.set_new_target(target_pose)
            self.robot.state.current_command = "Mover para interceptar"
            logger.debug(f"{self.name}: Novo alvo de interceptação definido em {target_pose}")
            return py_trees.common.Status.SUCCESS
        logger.warning(f"{self.name}: Não foi possível calcular o ponto de interceptação.")
        return py_trees.common.Status.FAILURE

class CalculateBasePosition(py_trees.behaviour.Behaviour):
    """Calcula a posição defensiva padrão (base) e define como alvo."""
    def __init__(self, robot: Bob, name: str = "Calcular Posição Base"):
        super().__init__(name)
        self.robot = robot
        self.base_position = Pose2D(-1800.0, 0.0)

    def update(self) -> py_trees.common.Status:
        self.robot.set_new_target(self.base_position)
        self.robot.state.current_command = "Retornando para a base"
        return py_trees.common.Status.SUCCESS
    
# ===================================================================================== #
# FUNÇÃO PRINCIPAL PARA CONSTRUIR A ÁRVORE
# ===================================================================================== #

def get_defender_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    """
    Monta e retorna a árvore de comportamento completa para o papel de Defensor.
    """
    # --- 1. Ramo de Interceptação (Máxima Prioridade) ---
    intercept_branch = py_trees.composites.Sequence(
        name="Ramo: Interceptar Ameaça de Gol",
        memory=True,
        children=[
            Ball_moving_towards_goal(name="Bola Indo Para o Gol?"),
            CalculateInterceptPosition(robot),
            cb.actions.Move_node(robot, name="Executar Movimento"),
        ],
    )

    # --- 2. Ramo de Bloqueio de Ameaça ---
    is_there_a_threat = py_trees.composites.Selector(
        name="Há Ameaça na Área?",
        memory=False,
        children=[
            Opponent_has_ball_in_danger_zone(name="Oponente com Bola na Zona Perigosa?"),
            Ball_in_defensive_area(name="Bola na Nossa Área de Defesa?"),
        ],
    )

    block_threat_branch = py_trees.composites.Sequence(
        name="Ramo: Bloquear Ameaça na Área",
        memory=True,
        children=[
            is_there_a_threat,
            CalculateDefensivePosition(robot),
            # CORREÇÃO: Outra nova instância do Move_node aqui
            cb.actions.Move_node(robot, name="Executar Movimento"),
        ],
    )
    
    # --- 3. Ramo Padrão (Fallback) ---
    go_to_base_position_branch = py_trees.composites.Sequence(
        name="Ramo: Voltar para Base",
        memory=True,
        children=[
            CalculateBasePosition(robot),
            cb.actions.Move_node(robot, name="Executar Movimento"),
        ],
    )

    # --- Nó Raiz (Selector de Prioridades) ---
    root = py_trees.composites.Selector(
        name="Comportamento do Defensor",
        memory=True,
        children=[
            intercept_branch,
            block_threat_branch,
            go_to_base_position_branch,
        ],
    )
    
    # --- Monta a árvore final ---
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.setup(robot=robot)
    return behaviour_tree