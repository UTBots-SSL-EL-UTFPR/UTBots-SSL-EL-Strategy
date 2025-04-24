import numpy as np
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial import distance
from utils.pose2D import Pose2D  # Importa a classe Pose2D



#Para rodar usar o comando      python3 -m motion.veronoi
#com o terminal na pasta        UTBots-SSL-EL-Strategy

class VoronoiGraph:
    def __init__(self, points):
        """
        Inicializa o grafo baseado no diagrama de Voronoi.
        :param points: Lista de pontos iniciais para o diagrama de Voronoi.
        """
        self.points = np.array(points)
        self.vor = Voronoi(self.points)
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
        Adiciona um ponto externo ao grafo, conectando-o ao vértice mais próximo.
        :param point: Coordenadas do ponto a ser adicionado.
        :param point_name: Nome do ponto no grafo.
        :return: Índice do vértice mais próximo.
        """
        closest_vertex = np.argmin([distance.euclidean(point, v) for v in self.vor.vertices])
        dist_to_vertex = distance.euclidean(point, self.vor.vertices[closest_vertex])
        self.graph.add_node(point_name, pos=point)
        self.graph.add_edge(point_name, closest_vertex, weight=dist_to_vertex)
        return closest_vertex

    def find_shortest_path(self, start_name, end_name):
        """
        Encontra o menor caminho entre dois pontos no grafo.
        :param start_name: Nome do ponto inicial.
        :param end_name: Nome do ponto final.
        :return: Lista de pontos do menor caminho como instâncias de Pose2D.
        """
        shortest_path = nx.shortest_path(self.graph, source=start_name, target=end_name, weight="weight")
        return [
            Pose2D(*self.graph.nodes[node]["pos"]) if isinstance(node, str) else Pose2D(*self.vor.vertices[node])
            for node in shortest_path
        ]

    def visualize(self, start_point, end_point, shortest_path_coords, output_file="voronoi_path_output.png"):
        """
        Visualiza o grafo, os pontos e o menor caminho.
        :param start_point: Coordenadas do ponto inicial.
        :param end_point: Coordenadas do ponto final.
        :param shortest_path_coords: Coordenadas do menor caminho.
        :param output_file: Nome do arquivo de saída para salvar a imagem.
        """
        pos = {i: v for i, v in enumerate(self.vor.vertices)}  # Posições dos vértices do Voronoi
        pos["start"] = start_point  # Adiciona a posição do ponto inicial
        pos["end"] = end_point      # Adiciona a posição do ponto final

        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw(self.graph, pos=pos, with_labels=True, ax=ax, node_color='lightblue')
        plt.plot(self.points[:, 0], self.points[:, 1], 'ro', label="Pontos Voronoi")
        plt.plot(start_point[0], start_point[1], 'go', label="Ponto Inicial")
        plt.plot(end_point[0], end_point[1], 'bo', label="Ponto Final")

        # Extrai os atributos x e y de cada Pose2D no caminho
        path_x = [pose.x for pose in shortest_path_coords]
        path_y = [pose.y for pose in shortest_path_coords]

        # Plota o menor caminho
        plt.plot(path_x, path_y, 'r-', label="Menor Caminho")
        plt.xlim(0, 4500)
        plt.ylim(0, 3000)
        plt.title("Grafo baseado no Diagrama de Voronoi com Caminho")
        plt.legend()
        plt.savefig(output_file)
        plt.show()


if __name__ == '__main__':
    # Pontos iniciais do Voronoi
    points = [[500, 500], [4000, 500], [2000, 2500], [3000, 1000], [1500, 1500], [3500, 2700], [500, 2900]]

    # Pontos de início e fim (fora do Voronoi)
    start_point = np.array([100, 100])
    end_point = np.array([4400, 2900])

    # Cria o grafo baseado no diagrama de Voronoi
    voronoi_graph = VoronoiGraph(points)

    # Adiciona os pontos de início e fim ao grafo
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    # Encontra o menor caminho entre os dois pontos
    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Converte o caminho para uma lista de Pose2D
    path_as_pose2d = shortest_path_coords

    # Exibe os pontos do caminho como Pose2D
    for pose in path_as_pose2d:
        print(f"Pose2D(x={pose.x}, y={pose.y})")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)