# bob_state.py

# bob_state.py

from core.Field import Field
from core.blackboard import Blackboard_Manager
from core.Field import RobotID
class Bob_State:
    """
    Guarda o estado dinâmico do robô e o atualiza a partir das leituras do campo.
    """

    def __init__(self, robot_id: RobotID):
        self.blackboard = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.position = (0.0, 0.0)
        self.velocity = (0.0, 0.0)
        self.orientation = 0.0
        self.target_position = None
        self.active_function = None
        self.current_command = None
        self.has_ball = False
        self.field = Field.get_instance()  # Singleton do campo

    def update(self):
        """
        Atualiza o estado com base nos dados fornecidos pela classe Field.
        """
        self.position = self.field.get_robot_position(self.robot_id)
        self.velocity = self.field.get_robot_velocity(self.robot_id)
        self.orientation = self.field.get_robot_orientation(self.robot_id)
        self.has_ball = self.field.check_possession(self.robot_id)
        #gerar flags de mudança
        #enviar flags para blackboard
    def set_position(self, x: float, y: float):
        """
        Atualiza a posição atual do robô.
        """
        self.position = (x, y)

    def set_velocity(self, vx: float, vy: float):
        """
        Atualiza a velocidade atual do robô.
        """
        self.velocity = (vx, vy)

    def set_orientation(self, angle: float):
        """
        Atualiza a orientação do robô.
        """
        self.orientation = angle

    def set_target_position(self, x: float, y: float):
        """
        Define a posição alvo para navegação.
        """
        self.target_position = (x, y)

    def reset(self):
        """
        Restaura o estado para valores padrão.
        """
        self.position = (0.0, 0.0)
        self.velocity = (0.0, 0.0)
        self.orientation = 0.0
        self.target_position = None
        self.active_function = None
        self.current_command = None
        self.has_ball = False