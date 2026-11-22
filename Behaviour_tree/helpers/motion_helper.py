from collections import deque

from utils.defines import BALL_RADIUS, ROBOT_RADIUS
from utils.pose2D import Pose2D

from .field_helper import FIELD_X_MAX, FIELD_X_MIN, FIELD_Y_MAX, FIELD_Y_MIN
from .positioning_helper import PositioningHelper


class MotionHelper:
    @classmethod
    def find_shortest_path(
        cls,
        start: Pose2D,
        end: Pose2D,
        obstacules: list[Pose2D],
        ball: Pose2D | None = None,
    ) -> list[Pose2D]:

        step = 20  # Resolução da grade (ajuste conforme necessário)
        # Limita a busca ao campo (+ margem). Sem isso, se o destino estiver ocupado (por
        # exemplo, em cima de outro robô) a BFS nunca termina e trava a estratégia inteira.
        margin = 300
        x_min, x_max = (FIELD_X_MIN - margin) // step, (FIELD_X_MAX + margin) // step
        y_min, y_max = (FIELD_Y_MIN - margin) // step, (FIELD_Y_MAX + margin) // step
        start_cell = (int(start.x // step), int(start.y // step))
        end_cell = (int(end.x // step), int(end.y // step))

        # BFS tradicional
        queue = deque([start_cell])
        visited = {start_cell: None}

        while queue:
            current = queue.popleft()
            if current == end_cell:
                # Reconstrói caminho
                path_rev = []
                while current is not None:
                    cx, cy = current
                    path_rev.append(Pose2D(cx * step, cy * step))
                    current = visited[current]
                return list(reversed(path_rev))

            cx, cy = current
            # Movimentos 8-direções (ou 4, se preferir)
            for nx, ny in [
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1),
                (cx + 1, cy + 1),
                (cx - 1, cy - 1),
                (cx + 1, cy - 1),
                (cx - 1, cy + 1),
            ]:
                if not (x_min <= nx <= x_max and y_min <= ny <= y_max):
                    continue
                if (nx, ny) not in visited:
                    wx, wy = nx * step, ny * step
                    if PositioningHelper.is_valid_placement(
                        wx, wy, obstacules, ROBOT_RADIUS
                    ):

                        if ball and not PositioningHelper.is_valid_placement(
                            wx, wy, [ball], BALL_RADIUS
                        ):
                            continue

                        visited[(nx, ny)] = current  # type: ignore
                        queue.append((nx, ny))

        return [start]
