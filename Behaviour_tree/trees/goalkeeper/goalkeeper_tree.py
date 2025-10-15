"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""

import logging

import py_trees

from Behaviour_tree import helpers as hp
from Behaviour_tree.commom_behaviours.actions import MovimentoUnico, RecuperarBola 
from Behaviour_tree.commom_behaviours.condition import BolaSegura, FoesHaveBall , HasBall
from Behaviour_tree.commom_behaviours.sub_trees.kick_subtree import get_kick_subtree
from Behaviour_tree.robot.bob import Bob

from Behaviour_tree.core.World_State import World_State
from ...core.blackboard import Blackboard_Manager
from ...bob_manager import BobManager


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

    # caso de defesa comum e suas folhas======================================
    foesHasBall = FoesHaveBall()
    goalkeeperCommonPosition = GoalkeeperCommonPosition(robot)

    defesa_comum = py_trees.composites.Sequence(
        name="Defesa_Comum",
        memory=False,
        children=[goalkeeperCommonPosition],
    )

    goalkeeper_tree = py_trees.composites.Selector(
        name="GoalkeeperTree", memory=True, children=[kick, bola_solta, defesa_comum]
    )
    #caso Ultimo Homem e suas folhas=========================================
    checkLastMan = CheckLastMan(robot)
    follow_ball = followBall(robot)

    ultimo_homem = py_trees.composites.Sequence(
        name="Ultimo_Homem",
        memory=False,
        children=[checkLastMan, follow_ball],
    )
    

    #tem a bola==============================================================
    passe_obj = passe(robot)
    chutar = chute(robot)
    hasBall = HasBall(robot)

    tem_a_bola = py_trees.composites.Sequence(
        name="Tem_a_Bola", memory=False, children=[hasBall, passe_obj, chutar]
    )

    #Raiz da arvore==========================================================
    root = py_trees.composites.Selector(
        name="root", memory=False,children=[ ultimo_homem, tem_a_bola]
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

class CheckLastMan(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "CheckLastMan"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = hp.PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        bm = BobManager.get_instance()
        if bm.get_last_man_id() != None:
            
            if bm.get_last_man_id() == self.robot.state.robot_id:
                return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE

class followBall(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "followBall"):
        super().__init__(name)
        self.robot = robot
        self._pos_helper = hp.PositioningHelper.get_object()
        self._bb = Blackboard_Manager.get_instance()
    
    def setup(self, **kwargs) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """
        Faz o robô andar reto na direção da bola.
        """
        # Pega a posição atual da bola do mundo
        world_state = World_State.get_object()
        ball_position = world_state.get_ball_position()
        
        if ball_position is None:
            # Se não conseguir pegar a posição da bola, falha
            return py_trees.common.Status.FAILURE
        
        # Define a posição da bola como alvo
        self.robot.set_new_target(ball_position)
        
        # Usa movimento rápido para ir direto na direção da bola
        self.robot.fast_movement()

        return py_trees.common.Status.SUCCESS
