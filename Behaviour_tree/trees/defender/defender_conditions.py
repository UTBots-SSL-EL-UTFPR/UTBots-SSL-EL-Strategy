# Behaviour_tree/trees/defender/defender_conditions.py
import py_trees
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys

_bb = Blackboard_Manager.get_instance()

class IsBallInDefensiveHalf(py_trees.behaviour.Behaviour):
    """Verifica a flag que indica se a bola está no campo de defesa."""
    def __init__(self, name: str = "Bola no Campo de Defesa?"):
        super().__init__(name)

    def update(self) -> py_trees.common.Status:
        if _bb.get(BlackboardKeys.Flags.Defense.BALL_IN_DEFENSIVE_HALF):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE