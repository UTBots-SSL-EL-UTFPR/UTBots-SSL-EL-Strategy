"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""
from time import sleep
from py_trees.common import Status
from py_trees import logging as log_tree

import py_trees

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.World_State import World_State
import time
from Behaviour_tree.core.event_callbacks import BB_flags_and_values

navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions

#---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
#---------------------------------------------------------------------------------------#

class Action(py_trees.behaviour.Behaviour):
  def __init__(self, name):
    super(Action, self).__init__(name)

  def setup(self):
    self.logger.debug(f"Action::setup {self.name}")

  def initialise(self):
    self.logger.debug(f"Action::initialise {self.name}")

  def update(self):
    self.logger.debug(f"Action::update {self.name}")
    sleep(1)
    return Status.SUCCESS

  def terminate(self, new_status):
    self.logger.debug(f"Action::terminate {self.name} to {new_status}")
        

class Move_without_path(py_trees.behaviour.Behaviour):
    """
    Move até um ponto único definido no Blackboard.
    Retorna RUNNING até 'at_target' ser True, SUCCESS quando chegar, FAILURE se bloqueado.
    """

    def __init__(self, name, Robot:Bob, target):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.bb = Blackboard_Manager.get_instance()

    def update(self):

        self.robot
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.is_stuck}"
            ):
            return py_trees.common.Status.FAILURE
        if self.bb.get(
            f"{self.robot.robot_id}{navigation_flags.target_reached}"
            ):
            return py_trees.common.Status.SUCCESS
        
        #chamar função que calcula onde deve ir e retorna velocidade das rodas

        self.robot.move(0,0) 
        return py_trees.common.Status.RUNNING
    
class Move_oriented(py_trees.behaviour.Behaviour):

    def __init__(self, name):
        super().__init__(name)
        self.robot : Bob | None = None
        self.target: tuple[float, float]
        self.teta: float
        self.bb = Blackboard_Manager.get_instance()


    def setup(self, **kwargs) -> None:  
        self.robot = kwargs.get("bob")
        if self.robot:
            print(f"ROBO {self.robot.robot_id.name} na arvore")

    def initialise(self) -> None:
        print("inicialização do movimento")
    
    def update(self):
        if self.robot is None: 
            print("fudeu o robo nao existe")
            return
        
        if self.bb.get(
            f"{self.robot.robot_id.name}{navigation_flags.is_stuck}"
            ):
            return py_trees.common.Status.FAILURE

        #chegou
        if self.bb.get(
            f"{self.robot.robot_id.name}{navigation_flags.target_reached}"
            ):
            return py_trees.common.Status.SUCCESS

        # Ainda não chegou — controlador de movimento vai ler target e agir
        
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
        #Has_Ball
            if( Bob.valid_range(self.position,self.target)):
                    if(Bob.is_free()):
                        Bob.pass_to_teammate()

            #avaliar quao livre jogador if(d_min<1m)
                #não pode ter pessoas dentro de um raio X
                #não pode ter pessoas dentro de um raio' X no trajeto da bola
            #avaliar distancia OK
    
        #decidir
            #Se bola no goleiro
                #escolhemos o mais "livre"
                    #o jogador com maior raio X e raio' X
            #senao
                #passa para o nao goleiro
        

        
