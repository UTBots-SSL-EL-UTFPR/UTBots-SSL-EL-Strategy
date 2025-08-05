"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""
import py_trees
from robot.bob import Bob
from core.blackboard import Blackboard_Manager
from core.Field import Field


class move_to_position(py_trees.behaviour.Behaviour):
    """
    vai até algum lugar
    """
    def __init__(self, name: str, bob: Bob, target_x: float, target_y: float):
        # super(move_to_position, self).__init__(name)
        # self.bob = bob
        # self.target_x = target_x
        # self.target_y = target_y
        ...

    def update(self) -> py_trees.common.Status:
        """
        lógica do  movimento.
        Retorna RUNNING, SUCCESS ao chegar, FAILURE se falhar.
        """
        #chamar metodo classe bob
        # return py_trees.common.Status.FAILURE
        ...

           

class kick_ball(py_trees.behaviour.Behaviour):
    """
    Chuta
    """
    def __init__(self, name: str, robot_instance: Bob):
        #super(kick_ball, self).__init__(name)
        #self.robot = robot_instance
        ...
    def update(self) -> py_trees.common.Status:
        """
        Executa a lógica de chute.
        Retorna SUCCESS se chutar, FAILURE se não tiver a posse da bola.
        """
        # if self.robot.kick_ball():
        #     return py_trees.common.Status.SUCCESS
        ...


class Conduz_bola(py_trees.behaviour.Behaviour):
    """
    nao sei se rola
    """
    def __init__(self, name: str, robot_instance: Bob):
        super(Conduz_bola, self).__init__(name)
        self.robot = robot_instance


    def update(self) -> py_trees.common.Status:
        """
        Executa a lógica de drible.
        Retorna SUCCESS se driblar, FAILURE se não tiver a posse da bola.
        """
        # if self.robot.dribble():
        #     return py_trees.common.Status.SUCCESS

        ...


class Stop_robot(py_trees.behaviour.Behaviour):
    """
    STOP
    """
    def __init__(self, name: str, robot_instance: Bob):
        # super(Stop_robot, self).__init__(name)
        # self.robot = robot_instance
         ...

    def update(self) -> py_trees.common.Status:
        """
        para o bob. Sempre retorna SUCCESS.
        """
        #self.bob.stop()?
        #return py_trees.common.Status.SUCCESS
        ...

class Set_posse_bola(py_trees.behaviour.Behaviour):
    """
    verifica posse de bola e seta bob
    """
    def __init__(self, name: str, robot_instance: Bob, status: bool):
        # super(Set_posse_bola, self).__init__(name)
        # self.robot = robot_instance
        # self.status = status
        ...

    def update(self):
        # self.robot.set_has_ball(self.status)
        # return py_trees.common.Status.SUCCESS
        ...
    import py_trees

#-------------------------------------------------------------------------#
#                                Coisas Reais                             #
#-------------------------------------------------------------------------#

class SetTeamStrategy(py_trees.behaviour.Behaviour):
    """
    Define a estratégia global do time com base na posição da bola.
    Escreve em 'team_strategy' no blackboard.
    """

    def __init__(self, name="SetTeamStrategy"):
        super().__init__(name)
        self.bb = Blackboard_Manager.get_instance()

    def update(self):
        ball_pos = Field.get_ball_position()

        if ball_pos[0] < -0.5:
            strategy = "attack"
        elif ball_pos[0] > 0.5:
            strategy = "defend"
        else:
            strategy = "hold"

        self.bb.set("team_strategy", strategy)
        return py_trees.common.Status.SUCCESS


