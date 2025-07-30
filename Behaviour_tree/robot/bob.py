# bob.py

import time
from .bob_state import Bob_State
from .bob_config import Bob_Config
from core.Field import RobotID
class Bob:
    """
    Classe que representa um robô SSL.

    Esta classe abstrai o robô como um agente controlável,
    com acesso à configuração física e ao estado dinâmico.

    :param robot_id: Identificador único do robô
    """

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id
        self.config = Bob_Config(robot_id)
        self.state = Bob_State(robot_id)
        self._has_ball = False

    def move(self, x: float, y: float) -> bool:
        """
        Move o robô até a posição (x, y).

        :param x: coordenada X de destino
        :param y: coordenada Y de destino
        :return: True se o comando foi aceito
        """
        print(f"[{self.robot_id}] Movendo para ({x}, {y})")
        self.state.set_target_position(x, y)
        return True

    def kick_ball(self) -> bool:
        """
        Realiza o chute da bola, se tiver a posse.

        :return: True se o chute foi realizado
        """
        if not self._has_ball:
            print(f"[{self.robot_id}] Sem posse de bola para chutar.")
            return False
        print(f"[{self.robot_id}] Chutou a bola!")
        self._has_ball = False
        return True

    def rotate(self, angle: float) -> bool:
        """
        Rotaciona o robô para determinado ângulo (em radianos).

        :param angle: ângulo alvo
        :return: True se o comando foi aceito
        """
        print(f"[{self.robot_id}] Rotacionando para {angle} rad")
        self.state.set_orientation(angle)
        return True

    def set_has_ball(self, status: bool) -> None:
       ...
        
    def has_ball(self) -> bool:
        """
        Verifica se o robô possui a bola.

        :return: True se possui
        """
        return self._has_ball


        