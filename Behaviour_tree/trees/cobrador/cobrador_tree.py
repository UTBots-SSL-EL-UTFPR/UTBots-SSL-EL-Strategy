import logging
import py_trees
import math
from utils.pose2D import Pose2D
from Behaviour_tree import commom_behaviours as cb
from Behaviour_tree import helpers as hp
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob

from Behaviour_tree.trees.suporte_recuado import get_pivot_tree as pivot_tree


logger = logging.getLogger(__name__)

# ===================================================================================== #
#                  COMPORTAMENTOS ESPECÍFICOS PARA O PAPEL COBRADOR                     #
# ===================================================================================== #

class IsLastDefender(py_trees.behaviour.Behaviour):
    """
    Condição que verifica se este robô é o mais recuado da equipe.
    Retorna SUCCESS se for o mais recuado, FAILURE caso contrário.
    Este FAILURE é o que ativa o comportamento de pivô no Selector principal.
    """
    def __init__(self, robot: Bob, name: str = "Condicao: Sou o ultimo da defesa?"):
        super().__init__(name)
        self.robot = robot
        self.world_state = World_State()

    def update(self) -> py_trees.common.Status:
        my_pos = self.robot.get_position()
        if not my_pos:
            return py_trees.common.Status.FAILURE

        allies_pos = [pos for pos in self.world_state.get_all_team_position() if pos]
        
        if not allies_pos:
            
            return py_trees.common.Status.SUCCESS

        if all(my_pos.x <= other_pos.x for other_pos in allies_pos):
            return py_trees.common.Status.SUCCESS
        
        return py_trees.common.Status.FAILURE



class LastDefenderPosition(py_trees.behaviour.Behaviour):
    """
    Ação para posicionar o robô como "goleiro avançado"
    """
    def __init__(self, robot: Bob, distance_from_goal_line: float = 1.5, name: str = "Posicionar como Goleiro "):
        super().__init__(name)
        self.robot = robot
        self.distance_from_goal_line = distance_from_goal_line

    def update(self) -> py_trees.common.Status:
        ball_pos = self.world_state.ball.position
        
        our_goal_pos = hp.FieldHelper.get_team_goal_center()

        if not ball_pos or not our_goal_pos:
                
            return py_trees.common.Status.FAILURE

        goal_to_ball_vec = ball_pos - our_goal_pos
        
        
        vec_magnitude = math.sqrt(goal_to_ball_vec.x**2 + goal_to_ball_vec.y**2)

        if vec_magnitude < 0.01:
            forward_direction = 1 if our_goal_pos.x < 0 else -1
            offset = Pose2D(self.distance_from_goal_line * forward_direction, 0)
        else:
          
            norm_x = goal_to_ball_vec.x / vec_magnitude
            norm_y = goal_to_ball_vec.y / vec_magnitude
        
            offset_x = norm_x * self.distance_from_goal_line
            offset_y = norm_y * self.distance_from_goal_line
            offset = Pose2D(offset_x, offset_y)
            
        
        target_pos = our_goal_pos + offset

        if our_goal_pos.x < 0: 
            target_pos.x = max(target_pos.x, our_goal_pos.x + 0.1)
        else: 
            target_pos.x = min(target_pos.x, our_goal_pos.x - 0.1)

        self.robot.state.target_position = target_pos
        self.robot.set_new_target(target_pos)
       
        return py_trees.common.Status.SUCCESS


def get_last_defender_behaviour(robot: Bob) -> py_trees.behaviour.Behaviour:
    """
    Cria a sub-árvore de comportamento para o modo "último homem".
    É um goleiro simplificado que prioriza passar,chutar, disputar a bola e se posicionar.
    """
    passe = cb.get_pass_subtree(robot)
    kick= cb.get_kick_subtree(robot)
    contest_ball = cb.get_luta_pela_bola_sub_tree(robot)
    position_self = LastDefenderPosition(robot)

    
    defender_logic = py_trees.composites.Selector(
        name="Logica_Ultimo_Homem", memory=True,
        children=[passe,kick, contest_ball, position_self],
    )
    return defender_logic


# ===================================================================================== #
#                                  COBRADOR                                             #
# ===================================================================================== #

def get_cobrador_tree(robot: Bob) -> py_trees.trees.BehaviourTree:
    """
    Árvore principal para o Robô Cobrador.

  
    1.  **Último Defensor**: Se a condição `IsLastDefender` for SUCESSO.
    2.  **Pivô**: Se a condição `IsLastDefender` falhar, este é o comportamento padrão.
    """
    last_defender = py_trees.composites.Sequence(
        name="Ramo:  Ultimo Defensor", memory=False,
        children=[
            IsLastDefender(robot),
            get_last_defender_behaviour(robot)
        ],
    )

   
    pivot = pivot_tree(robot).root
    pivot.name = " Pivo ( Suporte Recuado)"


    # --- RAIZ DA ÁRVORE ---
    
    root_selector = py_trees.composites.Selector(
        name="COBRADOR", memory=True,
        children=[last_defender, pivot],
    )

   
    root = py_trees.trees.BehaviourTree(root_selector)
    root.setup()
    return root