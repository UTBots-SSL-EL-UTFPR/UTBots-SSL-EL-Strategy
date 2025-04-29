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
        Constrói o grafo conectando todos os vértices válidos do diagrama de Voronoi,
        garantindo que as arestas não cruzem nenhum ponto.
        """
        # Filtra vértices válidos dentro dos limites
        valid_vertices = [
            (i, v) for i, v in enumerate(self.vor.vertices)
            if 0 <= v[0] <= 4500 and 0 <= v[1] <= 3000
        ]
    
        # Conecta todos os vértices válidos, verificando se as arestas não cruzam pontos
        for i, v1 in valid_vertices:
            for j, v2 in valid_vertices:
                if i != j:  # Evita auto-conexões
                    # Verifica se a aresta entre v1 e v2 cruza algum ponto
                    if not self._edge_crosses_points(v1, v2):
                        dist = np.linalg.norm(v1 - v2)
                        self.graph.add_edge(i, j, weight=dist)
    
    def _edge_crosses_points(self, v1, v2):
        """
        Verifica se a aresta entre dois vértices cruza algum ponto.
        :param v1: Coordenadas do primeiro vértice.
        :param v2: Coordenadas do segundo vértice.
        :return: True se a aresta cruzar algum ponto, False caso contrário.
        """
        for point in self.points:
            # Calcula a distância do ponto à linha formada por v1 e v2
            dist = self._point_to_line_distance(point, v1, v2)
            if dist < 1e-6:  # Considera que cruza se a distância for muito pequena
                return True
        return False
    
    def _point_to_line_distance(self, point, v1, v2):
        """
        Calcula a distância de um ponto a uma linha definida por dois vértices.
        :param point: Objeto Pose2D representando o ponto.
        :param v1: Coordenadas do primeiro vértice.
        :param v2: Coordenadas do segundo vértice.
        :return: Distância do ponto à linha.
        """
        x0, y0 = point.x, point.y
        x1, y1 = v1
        x2, y2 = v2
        return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt((y2 - y1)**2 + (x2 - x1)**2)

    def add_point(self, point, point_name):
        """
        Adiciona um ponto externo ao grafo, conectando-o a todos os vértices válidos
        cujas arestas não cruzem nenhum ponto.
        :param point: Objeto Pose2D representando o ponto a ser adicionado.
        :param point_name: Nome do ponto no grafo.
        """
        # Adiciona o ponto ao grafo
        self.graph.add_node(point_name, pos=point)

        # Conecta o ponto a todos os vértices válidos
        for i, vertex in enumerate(self.vor.vertices):
            if 0 <= vertex[0] <= 4500 and 0 <= vertex[1] <= 3000:  # Apenas vértices válidos
                # Verifica se a aresta entre o ponto e o vértice cruza algum ponto
                if not self._edge_crosses_points((point.x, point.y), vertex):
                    dist_to_vertex = distance.euclidean([point.x, point.y], vertex)
                    self.graph.add_edge(point_name, i, weight=dist_to_vertex)

    def connect_external_points(self, point1, point2, name1, name2):
        """
        Conecta dois pontos externos diretamente, se a aresta entre eles não cruzar outros pontos.
        :param point1: Objeto Pose2D representando o primeiro ponto.
        :param point2: Objeto Pose2D representando o segundo ponto.
        :param name1: Nome do primeiro ponto no grafo.
        :param name2: Nome do segundo ponto no grafo.
        """
 
        # Verifica se a aresta entre os dois pontos não cruza outros pontos
        if not self._edge_crosses_points((point1.x, point1.y), (point2.x, point2.y)):
            dist = distance.euclidean([point1.x, point1.y], [point2.x, point2.y])
            self.graph.add_edge(name1, name2, weight=dist)

   

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
        plt.xlim(0, 4500)
        plt.ylim(0, 3000)
        plt.title("Grafo baseado no Diagrama de Voronoi com Caminho")
        plt.legend()
        plt.savefig(output_file)
        plt.show()


if __name__ == '__main__':
    # Pontos iniciais do Voronoi
    points = []
    start_point = Pose2D(100, 100)
    end_point = Pose2D(4400, 2900)

    for i in range(6):
        while True:
            x = random.randint(-400, 4000)
            y = random.randint(-400, 4000)
            new_point = Pose2D(x, y)
            # Garante que o ponto não seja igual ao start_point ou end_point
            if new_point.x != start_point.x or new_point.y != start_point.y:
                if new_point.x != end_point.x or new_point.y != end_point.y:
                    points.append(new_point)
                    break

    voronoi_graph = VoronoiGraph(points)

    # Adiciona os pontos de início e fim ao grafo
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")


    # Encontra o menor caminho entre os pontos de início e fim
    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Exibe os pontos do caminho como Pose2D
    for pose in shortest_path_coords:
        print(f"Pose2D(x={pose.x}, y={pose.y})")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)