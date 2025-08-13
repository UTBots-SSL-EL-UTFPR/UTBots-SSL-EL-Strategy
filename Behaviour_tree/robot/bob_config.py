# bob_config.py
from ..core.Field import RobotID
class Bob_Config:
    """
    Classe que representa as configurações fixas de um robô.

    Dados como dimensões físicas, velocidade máxima, PID, etc.
    São imutáveis e definidos com base em arquivos externos (.yaml, JSON, etc).

    :param robot_id: Identificador único do robô
    """

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id

        self.dimensions = {
            "radius": 0.18,
            "height": 0.15
        }
        self.max_speed = 2.0  #: Velocidade máxima (m/s)
        self.kick_power = 5.0 #: Potência de chute
        self.pid_gains = {
            "kp": 1.0,
            "ki": 0.0,
            "kd": 0.1
        }
        self.role = "attacker"  
        
    def get_dimensions(self):
        return self.dimensions

    def get_pid(self):
        return self.pid_gains

    def get_max_speed(self):
        return self.max_speed

    def get_kick_power(self):
        return self.kick_power
