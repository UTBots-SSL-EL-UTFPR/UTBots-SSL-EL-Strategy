from collections import deque

from utils.defines import BALL_RADIUS, ROBOT_RADIUS
from utils.pose2D import Pose2D

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
