from collections import deque
from math import sqrt
from utils.pose2D import Pose2D

class BestPath:
    def __init__(self):
        pass

    def _is_free(self, x, y, obstacules, raio):
        # Verifica se (x,y) está distante o suficiente de cada obstáculo
        for obs in obstacules:
            if sqrt((x - obs.x)**2 + (y - obs.y)**2) < raio * 2.2:
                return False
        return True

    def find_shortest_path(self, start, end, obstacules, raio):
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
                    path_rev.append(Pose2D(cx*step, cy*step))
                    current = visited[current]
                return list(reversed(path_rev))

            cx, cy = current
            # Movimentos 8-direções (ou 4, se preferir)
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1),
                           (cx+1, cy+1), (cx-1, cy-1), (cx+1, cy-1), (cx-1, cy+1)]:
                if (nx, ny) not in visited:
                    wx, wy = nx*step, ny*step
                    if self._is_free(wx, wy, obstacules, raio):
                        visited[(nx, ny)] = current
                        queue.append((nx, ny))

        return [start]  # Caso não encontre caminho
