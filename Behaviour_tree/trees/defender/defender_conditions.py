# Behaviour_tree/trees/defender/defender_conditions.py
import py_trees
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys

_bb = Blackboard_Manager.get_instance()

class IsBallAThreat(py_trees.behaviour.Behaviour):
    """Verifica a flag que indica se a bola é uma ameaça de gol iminente."""
    def __init__(self, name: str = "Ameaça de Gol Iminente?"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        if _bb.get(BlackboardKeys.Flags.Defense.BALL_IS_A_THREAT):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsOpponentWithBallInDangerZone(py_trees.behaviour.Behaviour):
    """Verifica a flag que indica se há um oponente perigoso com a bola."""
    def __init__(self, name: str = "Oponente Perigoso?"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        if _bb.get(BlackboardKeys.Flags.Defense.OPPONENT_WITH_BALL_IN_DANGER_ZONE):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsBallInDefensiveHalf(py_trees.behaviour.Behaviour):
    """Verifica a flag que indica se a bola está no campo de defesa."""
    def __init__(self, name: str = "Bola no Campo de Defesa?"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        if _bb.get(BlackboardKeys.Flags.Defense.BALL_IN_DEFENSIVE_HALF):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE