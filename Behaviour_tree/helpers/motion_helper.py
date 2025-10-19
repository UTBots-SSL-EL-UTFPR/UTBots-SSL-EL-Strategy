import math
import time
from collections import deque

import numpy as np

from utils import defines
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
        step = 20
        start_cell = (int(start.x // step), int(start.y // step))
        end_cell = (int(end.x // step), int(end.y // step))
        queue = deque([start_cell])
        visited = {start_cell: None}
        while queue:
            current = queue.popleft()
            if current == end_cell:
                path_rev = []
                while current is not None:
                    cx, cy = current
                    path_rev.append(Pose2D(cx * step, cy * step))
                    current = visited[current]
                return list(reversed(path_rev))
            cx, cy = current
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
                        wx, wy, obstacules, defines.LOGIC_ROBOT_RADIUS
                    ):

                        if ball and not PositioningHelper.is_valid_placement(
                            wx, wy, [ball], defines.LOGIC_BALL_RADIUS
                        ):
                            continue

                        visited[(nx, ny)] = current  # type: ignore
                        queue.append((nx, ny))

        return [start]

    @classmethod
    def motorVel(cls, q, phi):
        """
        Aqui é o modelo cinematico da gracia.
        {w} = referencial da roda
        {b} = referencial do robô
        {s} = referencial do mundo

        phi é o angulo atual do robo em relação a {s}

        essa funcao tem q receber um vetor com as velocidades em {s}:
            q = np.array([[w], [vx_s], [vy_s]], dtype=float)
        com isso, ela monta a matriz de transformação H e resolve:
            u = H @ q
        depois satura em [-u_max, u_max].

        retorna um vetor com as velocidades das rodas

        """

        h = np.zeros((defines.KINEMATIC_N_RODAS, 3))
        for i in range(defines.KINEMATIC_N_RODAS):
            Bi = defines.KINEMATIC_WHEELS_ANGLES[i]  # Ângulo entre {w} e {b}
            gammai = defines.KINEMATIC_GAMMA[i]
            hi = np.array(
                [
                    defines.KINEMATIC_ROBOT_RADIUS,
                    np.cos(Bi + phi + gammai),
                    np.sin(Bi + phi + gammai),
                ]
            )
            hi /= defines.KINEMATIC_WHEEL_RADIUS * np.cos(
                gammai
            )  # Operações compactadas
            h[i][0] = hi[0]
            h[i][1] = hi[1]
            h[i][2] = hi[2]
        u = h @ q
        u = np.clip(u, -120.0, 120.0)

        return u
