# bob.py

from .bob_state import Bob_State
from .bob_config import Bob_Config
from ...utils import utilsp
from foes import Foes_State
import math
from math import sqrt
from utils.Point2D import Point2D
from ..core.Field import RobotID
#--------------------------------------------DEFINES--------------------------------------------#
LOWER = 0
UPPER = 1
class Bob:
    """
    Classe que representa um robô SSL.

    Esta classe abstrai o robô como um agente controlável,
    com acesso à configuração física e ao estado dinâmico.

    :param robot_id: Identificador único do robô
    """

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id.value
        self.config = Bob_Config(robot_id)
        self.state = Bob_State(robot_id)
        self._has_ball = False
        self.foes: list[Foes_State] #TODO

    def move(self, vel_x: float, vel_y: float) -> bool:
        """
        Move o robô até a posição (x, y).

        :param x: coordenada X de destino
        :param y: coordenada Y de destino
        :return: True se o comando foi aceito
        """
        #TODO enviar comando para simulação 
        return True
    
    def move_oriented(self, vel_x: float, vel_y: float, teta: float) -> bool:
        """
        Move o robô até a posição (x, y), enquanto mantem uma orientação.

        :param x: coordenada X de destino
        :param y: coordenada Y de destino

        """
        #TODO nao sei se isso ta pronto K. 
        #TODO enviar comando para simulação
        self.state.set_target_position(x, y)
        return True

    def kick_ball(self) -> bool:
        #TODO enviar comando para simulação
        return True

    def rotate(self, angle: float) -> bool:
        #TODO ENVIAR COMANDO ROTATE (é melhor controlar com encoders)
        return True

    def set_has_ball(self, status: bool) -> None:
        """
        Define o estado de posse de bola.
        """
        self._has_ball = status

        
    def has_ball(self) -> bool:
        #TODO state.position ≃ ball.position
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
    
    def go_to_ball(self, ball_position: Point2D) -> bool:
        return self.move(ball_position.x, ball_position.y)
    
    def go_to_point_avoiding_obstacles(self, dest: Point2D, obstacules: list[Point2D], raio: float) -> bool:
        start = self.state.get_position()
        path = self.find_shortest_path(start, dest, obstacules, raio)
        if path and len(path) > 1:
            next_step = path[1]
            return self.move(next_step.x, next_step.y)
        else:
            return self.move(dest.x, dest.y)
        
    def shoot_to_goal(self, goal_position: Point2D) -> bool:
        if not self.has_ball():
            return False
        my_pos = self.state.get_position()
        dx = goal_position.x - my_pos.x
        dy = goal_position.y - my_pos.y
        angle_to_goal = math.atan2(dy, dx)
        self.rotate(angle_to_goal)
        return self.kick_ball()
    
    def mark_opponent(self, opponent_pos: Point2D, own_goal: Point2D) -> bool:
        # Posição entre oponente e o gol (interceptação simples)
        intercept_x = (opponent_pos.x + own_goal.x) / 2
        intercept_y = (opponent_pos.y + own_goal.y) / 2
        return self.move(intercept_x, intercept_y)
    
    def pass_to_teammate(self, teammate_pos: Point2D) -> bool:
        if not self.has_ball():
            return False
        my_pos = self.state.get_position()
        dx = teammate_pos.x - my_pos.x
        dy = teammate_pos.y - my_pos.y
        angle = math.atan2(dy, dx)
        self.rotate(angle)
        return self.kick_ball()

    def dribble_towards(self, target_pos: Point2D) -> bool:
        if not self.has_ball():
            return False
        return self.move(target_pos.x, target_pos.y)


    def is_visible(self):
        #TODO
        pass


    def valid_range(self, position1:tuple[float, float], position2:tuple[float, float], limit:tuple[float, float]):
        distance = utilsp.get_distance(position1, position2)
        if distance > limit[LOWER]  and distance < limit[UPPER]:
            return True
        return False

    def distance_nearest_foe(self):
        distances =[]
        for foe in  self.foes:
            distances.append(utilsp.get_distance(self.state.position, foe.position))
        self.nearest_foe = utilsp.min(distances)