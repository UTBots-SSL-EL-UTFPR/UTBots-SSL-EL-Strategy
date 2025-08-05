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
    
    def update_from_field_state(self, field_state):
        """
        Atualiza o estado interno da classe Field com base no FieldState mais recente.
        """
        self._robot_positions.clear()
        self._robot_velocities.clear()
        self._robot_orientations.clear()

        for robot_id, data in field_state.robots_blue.items():
            self._robot_positions[robot_id] = (data["x"], data["y"])
            self._robot_velocities[robot_id] = (data["vx"], data["vy"])
            self._robot_orientations[robot_id] = data.get("orientation", 0.0)

        for robot_id, data in field_state.robots_yellow.items():
            self._robot_positions[robot_id] = (data["x"], data["y"])
            self._robot_velocities[robot_id] = (data["vx"], data["vy"])
            self._robot_orientations[robot_id] = data.get("orientation", 0.0)

        if field_state.ball:
            self._ball_position = (field_state.ball["x"], field_state.ball["y"])


    #TODO FAZER METODOS REAIS DA RECEIVER #CADEDOTO
    
    
