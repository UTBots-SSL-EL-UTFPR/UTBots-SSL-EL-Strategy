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
        self.robot.move() 
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
        self.robot.move_oriented() 
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
        self.robot.move()
        return py_trees.common.Status.RUNNING