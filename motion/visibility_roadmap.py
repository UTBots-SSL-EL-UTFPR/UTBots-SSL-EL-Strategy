from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Circle
from utils.pose2D import Pose2D 
import numpy as np

#Para rodar usar o comando      python3 -m motion.visibility_roadmap
#com o terminal na pasta        UTBots-SSL-EL-Strategy

class Visibility_Roadmap:
    def __init__(self, goal: Pose2D, start: Pose2D, robot_radius: int, robot_margin: int):
        self.obstacles = [] #lista de Pose2D
        self.robot_size =robot_radius
        self.margin =robot_margin
        self.graph = nx.Graph()
        self.goal =goal
        self.start =start
        self.nodes = []

    def set_margin(self, margin):
        self.margin = margin

    def add_obstacle(self, position: Pose2D):
        self.obstacles.append(position)
        self.append_nodes(position)

    def append_nodes(self, position: Pose2D):
        for i in range(4):
            angle_deg = i * 90
            angle_rad = np.deg2rad(angle_deg)
            dx = (self.robot_size + self.margin) * np.cos(angle_rad)
            dy = (self.robot_size + self.margin) * np.sin(angle_rad)
            node_position = (position.x + dx, position.y + dy)
            if node_position not in self.nodes:
                self.nodes.append(node_position)
                self.graph.add_node(node_position)


    def is_visible(self, p1, p2):
        line = LineString([p1, p2])

        for obs in self.obstacles:
            circle = Point(obs.x, obs.y).buffer(self.robot_size + self.margin)

            if line.crosses(circle) or line.within(circle):
                return False
            
        return True

    def connect_vertices(self):
        for node in self.nodes:
            self.graph.add_node(node)

        for i, p1 in enumerate(self.nodes):
            for j in range(i + 1, len(self.nodes)):
                p2 = self.nodes[j]
                if self.is_visible(p1, p2):
                    dist = Point(p1).distance(Point(p2))
                    self.graph.add_edge(p1, p2, weight=dist)


    def build_Roadmap(self):
        start_pos = (self.start.x, self.start.y)
        goal_pos = (self.goal.x, self.goal.y)

        self.nodes.append(start_pos)
        self.nodes.append(goal_pos)

        for node in self.nodes:
            if node != start_pos and self.is_visible(start_pos, node):
                dist = Point(start_pos).distance(Point(node))
                self.graph.add_edge(start_pos, node, weight=dist)
            if node != goal_pos and self.is_visible(goal_pos, node):
                dist = Point(goal_pos).distance(Point(node))
                self.graph.add_edge(goal_pos, node, weight=dist)

        self.connect_vertices()

        path = nx.shortest_path(
        self.graph,
        source=(self.start.x, self.start.y),
        target=(self.goal.x, self.goal.y),
        weight='weight'
        )   

    def visualize_map(self):
        fig, ax = plt.subplots()

        for obs in self.obstacles:
            circle = Circle((obs.x, obs.y), self.robot_size + self.margin, color='gray', alpha=0.5)
            ax.add_patch(circle)

        for node in self.nodes:
            ax.plot(node[0], node[1], 'bo', markersize=5)  # Nós em azul

        ax.plot(self.start.x, self.start.y, 'go', markersize=8, label="Start")  # Start em verde
        ax.plot(self.goal.x, self.goal.y, 'ro', markersize=8, label="Goal")  # Goal em vermelho

        for p1, p2, data in self.graph.edges(data=True):
            x_vals = [p1[0], p2[0]]
            y_vals = [p1[1], p2[1]]
            ax.plot(x_vals, y_vals, 'k-', linewidth=1)  # Arestas em preto

        ax.set_xlim([min([n[0] for n in self.nodes]) - 10, max([n[0] for n in self.nodes]) + 10])
        ax.set_ylim([min([n[1] for n in self.nodes]) - 10, max([n[1] for n in self.nodes]) + 10])
        ax.set_aspect('equal', 'box')

        ax.set_title("Roadmap Visualization")
        ax.legend(loc="best")
        plt.savefig("test_roadmap")


def test_visibility_roadmap():
    # Definindo o start e goal
    start_pose = Pose2D(-3000, -1000)  # Posição inicial do robô (start)
    goal_pose = Pose2D(3000, 1500)   # Posição do objetivo (goal)

    # Definindo o raio e a margem do robô
    robot_radius = 100
    robot_margin = 50

    # Criando uma instância da classe Visibility_Roadmap
    mapa = Visibility_Roadmap(goal_pose, start_pose, robot_radius, robot_margin)

    # Adicionando alguns obstáculos (usando Pose2D como exemplo)
    mapa.add_obstacle(Pose2D(100, 300))  # Obstáculo em (20, 20)
    mapa.add_obstacle(Pose2D(2000, 1500))  # Obstáculo em (30, 30)
    mapa.add_obstacle(Pose2D(-300, 2000))  # Obstáculo em (40, 40)
    mapa.add_obstacle(Pose2D(0, -2000))  # Obstáculo em (40, 40)
    mapa.add_obstacle(Pose2D(1365, 450))  # Obstáculo em (30, 30)


    # Construindo o roadmap com start, goal e obstáculos
    mapa.build_Roadmap()

    # Visualizando o mapa gerado
    mapa.visualize_map()


if __name__ == '__main__':
    test_visibility_roadmap()

