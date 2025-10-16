"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""

import logging

import py_trees

from Behaviour_tree import helpers as hp
from Behaviour_tree.commom_behaviours.actions import MovimentoUnico, RecuperarBola
from Behaviour_tree.commom_behaviours.condition import BolaSegura, FoesHaveBall, HasBall
from Behaviour_tree.commom_behaviours.sub_trees.kick_subtree import get_kick_subtree
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob

from ...bob_manager import BobManager
from ...core.blackboard import Blackboard_Manager

# ---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
# ---------------------------------------------------------------------------------------#
logger = logging.getLogger(__name__)


def get_goalkeeper_tree(robot: Bob) -> py_trees.trees.BehaviourTree:

    kick = get_kick_subtree(robot)

    bola_segura = BolaSegura(robot)
    recuperar_bola = RecuperarBola(robot)
    movimento_unico = MovimentoUnico(robot)

    bola_solta = py_trees.composites.Sequence(
        name="Bola_Solta",
        memory=False,
        children=[bola_segura, recuperar_bola, movimento_unico],
    )
    goalkeeperCommonPosition = GoalkeeperCommonPosition(robot)

    defesa_comum = py_trees.composites.Sequence(
        name="Defesa_Comum",
        memory=False,
        children=[goalkeeperCommonPosition],
    )

    goalkeeper_tree = py_trees.composites.Selector(
        name="GoalkeeperTree", memory=True, children=[kick, bola_solta, defesa_comum]
    )
    root = py_trees.trees.BehaviourTree(goalkeeper_tree)
    root.setup()
    return root


class GoalkeeperCommonPosition(py_trees.behaviour.Behaviour):

    def __init__(self, robot: Bob, name: str = "GoalkeeperCommonPosition"):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        position = hp.StrategyHelper.get_goalkeeper_defense_position()
        if position is None:
            return py_trees.common.Status.FAILURE

        self.robot.state.target_position = position
        self.robot.fast_movement()

        return py_trees.common.Status.SUCCESS
