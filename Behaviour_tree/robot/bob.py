# bob.py

import time
from .bob_state import BobState
from .bob_config import Bob_Config

import math
from math import sqrt
from utils.Point2D import Point2D

class Bob:
    """
    Classe que representa um robô SSL.

    Esta classe abstrai o robô como um agente controlável,
    com acesso à configuração física e ao estado dinâmico.

    :param robot_id: Identificador único do robô
    """

    def __init__(self, robot_id: str):
        self.robot_id = robot_id
        self.config = Bob_Config(robot_id)
        self.state = BobState(robot_id)
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

#===================================================#
#==== metodos auxiliares para os metodos do BOB ====#
        

    @staticmethod
    def is_free(x: float, y: float, obstacules: list[Point2D], raio: float) -> bool:
        # Verifica se (x,y) está distante o suficiente de cada obstáculo
        for obs in obstacules:
            if sqrt((x - obs.x)**2 + (y - obs.y)**2) < raio * 2.2:
                return False
        return True

    def find_shortest_path(self, start: Point2D, end: Point2D, obstacules: list[Point2D], raio: float):
        from collections import deque
        step = 20  # Resolução da grade (ajuste conforme necessário)
        start_cell = (int(start.x // step), int(start.y // step))
        end_cell = (int(end.x // step), int(end.y // step))

        # BFS tradicional
        queue = deque([start_cell])
        visited = {start_cell: None}  # Armazena o pai para reconstruir rota

        while queue:
            current = queue.popleft()
            if current == end_cell:
                # Reconstrói caminho
                path_rev = []
                while current is not None:
                    cx, cy = current
                    path_rev.append(Point2D(cx*step, cy*step))
                    current = visited[current]
                return list(reversed(path_rev))

            cx, cy = current
            # Movimentos 8-direções (ou 4, se preferir)
            for nx, ny in [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1),
                (cx+1, cy+1), (cx-1, cy-1), (cx+1, cy-1), (cx-1, cy+1)
            ]:
                if (nx, ny) not in visited:
                    wx, wy = nx*step, ny*step
                    if Bob.is_free(wx, wy, obstacules, raio):
                        visited[(nx, ny)] = current
                        queue.append((nx, ny))

        return [start]  # Caso não encontre caminho