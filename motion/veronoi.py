import numpy as np
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial import distance
from utils.pose2D import Pose2D 


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
        Adiciona um ponto externo ao grafo, conectando-o ao vértice mais próximo.
        :param point: Objeto Pose2D representando o ponto a ser adicionado.
        :param point_name: Nome do ponto no grafo.
        :return: Índice do vértice mais próximo.
        """
        closest_vertex = np.argmin([distance.euclidean([point.x, point.y], v) for v in self.vor.vertices])
        dist_to_vertex = distance.euclidean([point.x, point.y], self.vor.vertices[closest_vertex])
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
            self.graph.nodes[node]["pos"] if isinstance(node, str) else Pose2D(*self.vor.vertices[node])
            for node in shortest_path
        ]

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
        plt.xlim(0, 4500)
        plt.ylim(0, 3000)
        plt.title("Grafo baseado no Diagrama de Voronoi com Caminho")
        plt.legend()
        plt.savefig(output_file)
        plt.show()


if __name__ == '__main__':
    # Pontos iniciais do Voronoi
    points = [Pose2D(500, 500), Pose2D(4000, 500), Pose2D(2000, 2500)]

    # Pontos de início e fim (fora do Voronoi)
    start_point = Pose2D(100, 100)
    end_point = Pose2D(4400, 2900)

    # Cria o grafo baseado no diagrama de Voronoi
    voronoi_graph = VoronoiGraph(points)

    # Adiciona os pontos de início e fim ao grafo
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    # Encontra o menor caminho entre os dois pontos
    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Exibe os pontos do caminho como Pose2D
    for pose in shortest_path_coords:
        print(f"Pose2D(x={pose.x}, y={pose.y})")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)