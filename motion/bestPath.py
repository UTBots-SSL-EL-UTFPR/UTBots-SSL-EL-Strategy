from math import sqrt
from utils.pose2D import Pose2D

class BestPath:
    def __init__(self):
        pass

    def find_shortest_path(self, start, end, obstacules, raio):
        """
        Gera uma trajetória do ponto start ao ponto end, desviando dos obstáculos.
        A trajetória não pode se aproximar mais do que raio * 2.2 dos obstáculos.
        :param start: Pose2D representando o ponto inicial.
        :param end: Pose2D representando o ponto final.
        :param obstacules: Lista de Pose2D representando os obstáculos.
        :param raio: Raio efetivo dos obstáculos.
        :return: Lista de Pose2D representando a trajetória ajustada.
        """
        trajectory = [start]  # Trajetória inicial começa no ponto inicial
        step_size = 10        # Tamanho do passo entre os pontos
        max_iterations = 1000 # Limite de iterações para evitar loops infinitos
        obstacle_radius = raio * 2.2  # Raio efetivo dos obstáculos

        # Inicializa a trajetória com pontos intermediários igualmente espaçados
        total_distance = sqrt((end.x - start.x)**2 + (end.y - start.y)**2)
        num_points = max(int(total_distance / step_size), 2)
        for i in range(1, num_points):
            ratio = i / float(num_points)
            x = start.x + (end.x - start.x) * ratio
            y = start.y + (end.y - start.y) * ratio
            trajectory.append(Pose2D(x, y))
        trajectory.append(end)

        # Itera para ajustar a trajetória
        for _ in range(max_iterations):
            new_trajectory = [trajectory[0]]  # O ponto inicial permanece fixo
            max_movement = 0

            # Atualiza os pontos intermediários (exceto start e end)
            for i in range(1, len(trajectory) - 1):
                current = trajectory[i]
                prev = trajectory[i - 1]
                next_point = trajectory[i + 1]

                # Força de atração para manter a suavidade da trajetória
                attraction_x = (prev.x + next_point.x) / 2 - current.x
                attraction_y = (prev.y + next_point.y) / 2 - current.y

                # Força de repulsão para evitar os obstáculos
                repulsion_x, repulsion_y = 0, 0
                for obstacle in obstacules:
                    dx = current.x - obstacle.x
                    dy = current.y - obstacle.y
                    distance_to_obstacle = sqrt(dx**2 + dy**2)

                    if distance_to_obstacle < obstacle_radius:
                        # Calcula a força de repulsão com intensidade maior para distâncias menores
                        repulsion_strength = (obstacle_radius - distance_to_obstacle) / obstacle_radius
                        repulsion_strength *= 50  # Ajuste da força de repulsão
                        if distance_to_obstacle > 0:  # Evita divisão por zero
                            repulsion_x += (dx / distance_to_obstacle) * repulsion_strength
                            repulsion_y += (dy / distance_to_obstacle) * repulsion_strength

                # Combina as forças de atração e repulsão
                new_x = current.x + attraction_x + repulsion_x
                new_y = current.y + attraction_y + repulsion_y

                # Garante que o ponto não entre na zona proibida dos obstáculos
                for obstacle in obstacules:
                    dx = new_x - obstacle.x
                    dy = new_y - obstacle.y
                    distance_to_obstacle = sqrt(dx**2 + dy**2)
                    if distance_to_obstacle < obstacle_radius:
                        adjustment = obstacle_radius - distance_to_obstacle
                        new_x += (dx / distance_to_obstacle) * adjustment
                        new_y += (dy / distance_to_obstacle) * adjustment

                new_point = Pose2D(new_x, new_y)
                move = sqrt((new_x - current.x)**2 + (new_y - current.y)**2)
                if move > max_movement:
                    max_movement = move
                new_trajectory.append(new_point)

            new_trajectory.append(trajectory[-1])  # O ponto final permanece fixo
            trajectory = new_trajectory

            # Verifica se a trajetória convergiu
            if max_movement < 0.1:
                break

        return trajectory
