"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""
import py_trees
from robot.bob import Bob
from core.blackboard import Blackboard_Manager
from core.Field import Field
import time
from core.event_callbacks import BB_flags_and_values

navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions

#---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
#---------------------------------------------------------------------------------------#


class Move_without_path(py_trees.behaviour.Behaviour):
    """
    Move até um ponto único definido no Blackboard.
    Retorna RUNNING até 'at_target' ser True, SUCCESS quando chegar, FAILURE se bloqueado.
    """

    def __init__(self, name, Robot:Bob):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.bb = Blackboard_Manager.get_instance()

    def update(self):
        #preso ou  sla, tem q ver isso ai
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.is_stuck}"
            ):
            return py_trees.common.Status.FAILURE

        #chegou
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.target_reached}"
            ):
            return py_trees.common.Status.SUCCESS

        # Ainda não chegou — controlador de movimento vai ler target e agir
        self.robot.move(0,0) 
        return py_trees.common.Status.RUNNING

class Move_oriented(py_trees.behaviour.Behaviour):

    def __init__(self, name, Robot:Bob):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.teta: float
        self.bb = Blackboard_Manager.get_instance()

    def update(self):
        #preso ou  sla, tem q ver isso ai
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.is_stuck}"
            ):
            return py_trees.common.Status.FAILURE

        #chegou
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.target_reached}"
            ):
            return py_trees.common.Status.SUCCESS

        # Ainda não chegou — controlador de movimento vai ler target e agir
        self.robot.move_oriented(0,0,0) 
        return py_trees.common.Status.RUNNING

class Move_follow_Path(py_trees.behaviour.Behaviour):

    def __init__(self, name, Robot:Bob):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.teta: float
        self.bb = Blackboard_Manager.get_instance()

    def update(self):
        #preso ou  sla, tem q ver isso ai
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.is_stuck}"
            ):
            return py_trees.common.Status.FAILURE
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.lost_path}"       
        ):
            return py_trees.common.Status.FAILURE
        #chegou
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.target_reached}"
            ):
            return py_trees.common.Status.SUCCESS

        # Ainda não chegou — controlador de movimento vai ler target e agir
        self.robot.move(0,0)
        return py_trees.common.Status.RUNNING
    


#---------------------------------------------------------------------------------------#
#                                           PASS                                        #
#---------------------------------------------------------------------------------------#

class Choose_who_to_pass(py_trees.behaviour.Behaviour):

    def __init__(self, Robot:Bob, name):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.bb = Blackboard_Manager.get_instance()
        self.position = self.bb.get(f"{Robot.robot_id}{positions.quadrant}")

    def update(self):
        #avaliar pos outros jogadores
            #avaliar quao livre jogador
                #não pode ter pessoas dentro de um raio X
                #não pode ter pessoas dentro de um raio' X no trajeto da bola
            #avaliar distancia OK
    
        #decidir
            #Se bola no goleiro
                #escolhemos o mais "livre"
                    #o jogador com maior raio X e raio' X
            #senao
                #passa para o nao goleiro
        ...

            
