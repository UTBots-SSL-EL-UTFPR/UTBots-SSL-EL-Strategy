def venoi():
    import numpy as np
    from scipy.spatial import Voronoi
    import matplotlib.pyplot as plt
    import networkx as nx

    points = np.array([[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5], [0.2, 0.7], [0.1,0.3]])

    vor = Voronoi(points)
    G = nx.Graph()

    for ridge in vor.ridge_vertices:
        if -1 not in ridge:  
            p1, p2 = ridge
            v1, v2 = vor.vertices[p1], vor.vertices[p2]
            dist = np.linalg.norm(v1 - v2)
            G.add_edge(p1, p2, weight=dist)

    fig, ax = plt.subplots()
    nx.draw(G, pos={i: v for i, v in enumerate(vor.vertices)}, with_labels=True, ax=ax, node_color='lightblue')
    plt.plot(points[:, 0], points[:, 1], 'ro')
    plt.title("Grafo baseado no Diagrama de Voronoi")
    plt.savefig("voronoi_output.png")

    
if __name__ == '__main__':
    venoi()