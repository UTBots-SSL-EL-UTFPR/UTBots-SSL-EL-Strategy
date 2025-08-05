import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial import distance
from utils.pose2D import Pose2D 
import random

#Para rodar usar o comando      python3 -m motion.veronoi
#com o terminal na pasta        UTBots-SSL-EL-Strategy

class VoronoiGraph:
    def __init__(self, points):
        """
        Inicializa o grafo baseado no diagrama de Voronoi.
        :param points: Lista de pontos iniciais para o diagrama de Voronoi (como objetos Pose2D).
        """
        self.points = [Pose2D(p.x, p.y) for p in points]
        self.vor = Voronoi([[p.x, p.y] for p in self.points])
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """
        Constrói o grafo a partir das arestas do diagrama de Voronoi.
        """
        for ridge in self.vor.ridge_vertices:
            if -1 not in ridge:  # Ignora arestas infinitas
                p1, p2 = ridge
                v1, v2 = self.vor.vertices[p1], self.vor.vertices[p2]
                dist = np.linalg.norm(v1 - v2)
                self.graph.add_edge(p1, p2, weight=dist)

    def add_point(self, point, point_name):
        """
        Adiciona um ponto externo ao grafo, conectando-o aos 3 vértices mais próximos.
        :param point: Objeto Pose2D representando o ponto a ser adicionado.
        :param point_name: Nome do ponto no grafo.
        :return: Lista de índices dos 3 vértices mais próximos.
        """
        # Calcula as distâncias do ponto para todos os vértices
        distances = [distance.euclidean([point.x, point.y], v) for v in self.vor.vertices]
        
        # Encontra os índices dos 3 vértices mais próximos
        closest_vertices = np.argsort(distances)[:3]
        
        # Adiciona o ponto ao grafo
        self.graph.add_node(point_name, pos=point)
        
        # Conecta o ponto aos 3 vértices mais próximos
        for vertex in closest_vertices:
            dist_to_vertex = distances[vertex]
            self.graph.add_edge(point_name, vertex, weight=dist_to_vertex)
        
        return closest_vertices


    def find_shortest_path(self, start_node, end_node):
        """
        Encontra o menor caminho entre dois pontos no grafo utilizando busca bidirecional.
        
        :param start_node: Nome do ponto inicial.
        :param end_node: Nome do ponto final.
        :return: Lista de pontos do menor caminho como instâncias de Pose2D.
        """
        try:
            lenght, path= nx.bidirectional_dijkstra(self.graph, source=start_node, target=end_node, weight="weight")
            print(lenght)
            return [
                self.graph.nodes[node]["pos"] if isinstance(node, str) else Pose2D(*self.vor.vertices[node])
                for node in path
            ]

        except nx.NetworkXNoPath:
            return []


    def visualize(self, start_point, end_point, shortest_path_coords, output_file="voronoi_path_output.png"):
        """
        Visualiza o grafo, os pontos e o menor caminho.
        :param start_point: Objeto Pose2D representando o ponto inicial.
        :param end_point: Objeto Pose2D representando o ponto final.
        :param shortest_path_coords: Lista de objetos Pose2D representando o menor caminho.
        :param output_file: Nome do arquivo de saída para salvar a imagem.
        """
        pos = {i: [v[0], v[1]] for i, v in enumerate(self.vor.vertices)}  # Posições dos vértices do Voronoi
        pos["start"] = [start_point.x, start_point.y]  # Adiciona a posição do ponto inicial
        pos["end"] = [end_point.x, end_point.y]       # Adiciona a posição do ponto final

        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw(self.graph, pos=pos, with_labels=True, ax=ax, node_color='lightblue')
        plt.plot([p.x for p in self.points], [p.y for p in self.points], 'ro', label="Pontos Voronoi")
        plt.plot(start_point.x, start_point.y, 'go', label="Ponto Inicial")
        plt.plot(end_point.x, end_point.y, 'bo', label="Ponto Final")

        # Extrai os atributos x e y de cada Pose2D no caminho
        path_x = [pose.x for pose in shortest_path_coords]
        path_y = [pose.y for pose in shortest_path_coords]

        # Plota o menor caminho
        plt.plot(path_x, path_y, 'r-', label="Menor Caminho")
        plt.xlim(-4500, 4500)
        plt.ylim(-3000, 3000)
        plt.title("Grafo baseado no Diagrama de Voronoi com Caminho")
        plt.legend()
        plt.savefig("test_veronoi")
        plt.show()


if __name__ == '__main__':
    # Pontos iniciais do Voronoi
    points = []
    points.append(Pose2D(100, 300))  # Obstáculo em (20, 20)
    points.append(Pose2D(2000, 1500))  # Obstáculo em (30, 30)
    points.append(Pose2D(-300, 2000))  # Obstáculo em (40, 40)
    points.append(Pose2D(0, -2000))  # Obstáculo em (40, 40)
    points.append(Pose2D(1365, 450))  # Obstáculo em (30, 30)

    start_point = Pose2D(-3000, -1000)
    end_point = Pose2D(3000, 1500)

    voronoi_graph = VoronoiGraph(points)
    fig = voronoi_plot_2d(voronoi_graph.vor)
    plt.savefig("diagrama_voronoi.png", dpi=100, bbox_inches='tight')
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Exibe os pontos do caminho como Pose2D
    for pose in shortest_path_coords:
        print(f"Pose2D(x={pose.x}, y={pose.y})")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)