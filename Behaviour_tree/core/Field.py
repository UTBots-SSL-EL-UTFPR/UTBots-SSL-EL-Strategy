# field.py

from enum import Enum
# robot_id.py

from enum import Enum

class RobotID(Enum):
    Kamiji = "Kamiji"
    Defender = "Defender"
    Goalkeeper = "GOALKEEPER"


class Field:
    _instance = None

    def __init__(self):
        # Inicializa com dicionários preenchidos pelo receiver
        self._robot_positions = {}
        self._robot_velocities = {}
        self._robot_orientations = {}
        self._ball_position = (0.0, 0.0)
        self._ball_possession = {}

    @staticmethod
    def get_instance():
        if Field._instance is None:
            Field._instance = Field()
        return Field._instance

    def get_robot_position(self, robot_id: RobotID):
        return self._robot_positions.get(robot_id, (0.0, 0.0))

    def get_robot_velocity(self, robot_id: RobotID):
        return self._robot_velocities.get(robot_id, (0.0, 0.0))

    def get_robot_orientation(self, robot_id: RobotID):
        return self._robot_orientations.get(robot_id, 0.0)

    def get_ball_position(self):
        return self._ball_position

    def check_possession(self, robot_id: RobotID):
        return self._ball_possession.get(robot_id, False)

    #TODO FAZER METODOS REAIS DA RECEIVER #CADEDOTO
    
    
