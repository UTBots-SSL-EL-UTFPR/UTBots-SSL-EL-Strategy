# Behaviour_tree/trees/defender/defender_tree.py
import py_trees
import time
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

from .defender_conditions import IsBallInDefensiveHalf
from .defender_strategy_helper import DefenderStrategyHelper

POSITIONAL_TOLERANCE = 150.0 # Aumentado um pouco para dar mais estabilidade

class SmartMarking(py_trees.behaviour.Behaviour):
    """
    Implementa a lógica de "Alvo Fixo" para um movimento estável.
    """
    def __init__(self, robot: Bob, name: str = "Marcação Inteligente"):
        super().__init__(name)
        self.robot = robot
        # Variável para armazenar o alvo "congelado"
        self._locked_target: Pose2D | None = None

    def update(self) -> py_trees.common.Status:
        # 1. Calcula o alvo estratégico ideal a cada ciclo
        strategic_target = DefenderStrategyHelper.get_aggressive_marking_pose()
        if not strategic_target:
            self.robot.state.current_command = "Falha ao Calcular Posição"
            self._locked_target = None # Limpa o alvo fixo se a estratégia falhar
            return py_trees.common.Status.FAILURE
        
        # 2. Calcula a distância do robô até o alvo estratégico
        distance_to_strategic_target = self.robot.state.position.distance_to(strategic_target)

        # ============================================================================== #
        # LÓGICA DO "ALVO FIXO"
        # ============================================================================== #
        if distance_to_strategic_target > POSITIONAL_TOLERANCE:
            # FASE 1: APROXIMAÇÃO RÁPIDA (Longe do Alvo)
            # Estamos fora da zona de precisão, então não há alvo fixo.
            self._locked_target = None
            # O alvo do robô é o alvo estratégico mais recente.
            self.robot.state.target_position = strategic_target
            self.robot.state.current_command = "Aproximando da Posição"
            self.robot.fast_movement()
        else:
            # FASE 2: ALINHAMENTO PRECISO (Perto do Alvo)
            # Se acabamos de entrar na zona, "congelamos" o alvo.
            if self._locked_target is None:
                self._locked_target = strategic_target
            
            # O robô agora trabalha EXCLUSIVAMENTE com o alvo fixo.
            self.robot.state.target_position = self._locked_target
            self.robot.state.current_command = "Ajustando Ângulo Final"
            self.robot.precision_movement()

        return py_trees.common.Status.RUNNING

# (O resto do arquivo - ReturnToBase e get_defender_tree - está correto e não muda)
class ReturnToBase(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Retornar para Base"):
        super().__init__(name)
        self.robot = robot
        self.base_position = DefenderStrategyHelper.get_base_position_by_id(robot.robot_id)
    def update(self) -> py_trees.common.Status:
        self.robot.state.target_position = self.base_position
        self.robot.state.current_command = "Retornando para a Base"
        self.robot.fast_movement()
        return py_trees.common.Status.RUNNING

def get_defender_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    defensive_branch = py_trees.composites.Sequence(
        "Ramo: Defender", memory=False,
        children=[IsBallInDefensiveHalf(), SmartMarking(robot)]
    )
    base_branch = ReturnToBase(robot)
    root = py_trees.composites.Selector(
        "Comportamento do Defensor", memory=False,
        children=[defensive_branch, base_branch]
    )
    return py_trees.trees.BehaviourTree(root)