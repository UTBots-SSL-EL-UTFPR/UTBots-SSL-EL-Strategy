import numpy as np
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial import distance


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
        :return: Lista de coordenadas do menor caminho.
        """
        shortest_path = nx.shortest_path(self.graph, source=start_name, target=end_name, weight="weight")
        return [
            self.graph.nodes[node]["pos"] if isinstance(node, str) else self.vor.vertices[node]
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

        fig, ax = plt.subplots()
        nx.draw(self.graph, pos=pos, with_labels=True, ax=ax, node_color='lightblue')
        plt.plot(self.points[:, 0], self.points[:, 1], 'ro', label="Pontos Voronoi")
        plt.plot(start_point[0], start_point[1], 'go', label="Ponto Inicial")
        plt.plot(end_point[0], end_point[1], 'bo', label="Ponto Final")
        path_coords = np.array(shortest_path_coords)
        plt.plot(path_coords[:, 0], path_coords[:, 1], 'r-', label="Menor Caminho")
        plt.title("Grafo baseado no Diagrama de Voronoi com Caminho")
        plt.legend()
        plt.savefig(output_file)
        plt.show()


if __name__ == '__main__':
    # Pontos iniciais do Voronoi
    points = [[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5], [0.2, 0.7], [0.1, 0.3]]

    # Pontos de início e fim (fora do Voronoi)
    start_point = np.array([2.2, 0.2])
    end_point = np.array([0, 1.3])

    # Cria o grafo baseado no diagrama de Voronoi
    voronoi_graph = VoronoiGraph(points)

    # Adiciona os pontos de início e fim ao grafo
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    # Encontra o menor caminho entre os dois pontos
    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)