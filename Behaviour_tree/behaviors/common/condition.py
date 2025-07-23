import py_trees
from robot.bob import Bob

class is_ball_visible(py_trees.behaviour.Behaviour):
    """
    Condição: verifica se nao ha obs entre bob e bola
    """
    def __init__(self, name: str):
    #    super(is_ball_visible, self).__init__(name)
        ...


    def update(self) -> py_trees.common.Status:
        """
        Verifica a condição. Retorna SUCCESS ou FAILURE.
        """
        #return py_trees.common.Status.SUCCESS?
        ...
        

class is_ball_reachable(py_trees.behaviour.Behaviour):
    """
    Condição: Verifica se o bob esta proximo e rapido o suficiente para alcançar a bola
    """
    def __init__(self, name: str, robot_instance: Bob, threshold: float = 4445545):
        #super(is_ball_reachable, self).__init__(name)
        #self.robot = robot_instance
        #self.threshold = threshold
        ...


    def update(self) -> py_trees.common.Status:
        """
        Calcula a distância e retorna SUCCESS se perto, FAILURE caso contrário.
        """
        # return py_trees.common.Status.FAILURE
        ...

class is_goal_open(py_trees.behaviour.Behaviour):
    """
    Condição: Verifica se o gol ta livre para chutar (dan).
    """
    def __init__(self, name: str):
        #super(is_goal_open, self).__init__(name)
        ...

    def update(self) -> py_trees.common.Status:
        """
        Verifica a condição do gol. Retorna SUCCESS ou FAILURE.
        """
        #return py_trees.common.Status.FAILURE
        ...

class tem_posse_bola(py_trees.behaviour.Behaviour):
    """
    Condição: Verifica se o robô tem a posse da bola.
    """
    def __init__(self, name: str, robot_instance: Bob):
        #super(tem_posse_bola, self).__init__(name)
        #self.robot = robot_instance
        ...


    def update(self) -> py_trees.common.Status:
        #TODO 
        ...