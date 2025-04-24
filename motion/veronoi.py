import random
import numpy as np
from scipy.spatial import Voronoi

# Parâmetros
WIDTH, HEIGHT = 1350, 900
MARGIN = 35
NUM_OBSTACLES = 5
OBSTACLE_RADIUS = 18
EDGE_SAMPLE_DIST = 150

# Gerar obstáculos aleatórios
obstacles = []
def random_circle():
    while True:
        x = random.randint(MARGIN + OBSTACLE_RADIUS, WIDTH - MARGIN - OBSTACLE_RADIUS)
        y = random.randint(MARGIN + OBSTACLE_RADIUS, HEIGHT - MARGIN - OBSTACLE_RADIUS)
        if all(np.hypot(x - cx, y - cy) > 2 * OBSTACLE_RADIUS for cx, cy in obstacles):
            return (x, y)
for _ in range(NUM_OBSTACLES):
    obstacles.append(random_circle())

# Amostrar pontos nas paredes
boundaries = []
x_min, x_max = MARGIN, WIDTH - MARGIN
y_min, y_max = MARGIN, HEIGHT - MARGIN
for x in range(x_min, x_max + 1, EDGE_SAMPLE_DIST):
    boundaries.extend([(x, y_min), (x, y_max)])
for y in range(y_min, y_max + 1, EDGE_SAMPLE_DIST):
    boundaries.extend([(x_min, y), (x_max, y)])

sites = np.array(obstacles + boundaries)
vor = Voronoi(sites)

nodes = []
edges = []

# Checar se segmento é inválido
def segment_invalid(p1, p2):
    vec = p2 - p1
    steps = max(1, int(np.linalg.norm(vec)))
    for i in range(steps + 1):
        pt = p1 + vec * (i / steps)
        if not (x_min <= pt[0] <= x_max and y_min <= pt[1] <= y_max):
            return True
        if any((pt[0] - cx)**2 + (pt[1] - cy)**2 < OBSTACLE_RADIUS**2 for cx, cy in obstacles):
            return True
    return False

# Adquirir nós válidos
for v in vor.vertices:
    if (x_min <= v[0] <= x_max and y_min <= v[1] <= y_max
        and not any((v[0] - cx)**2 + (v[1] - cy)**2 < OBSTACLE_RADIUS**2 for cx, cy in obstacles)):
        nodes.append(v)

# Construir arestas válidas
def find_index(vec):
    for i, n in enumerate(nodes):
        if np.allclose(vec, n):
            return i
    return -1

for ridge in vor.ridge_vertices:
    if -1 in ridge:
        continue
    p1 = vor.vertices[ridge[0]]
    p2 = vor.vertices[ridge[1]]
    if list(p1) in nodes and list(p2) in nodes and not segment_invalid(p1, p2):
        i1 = find_index(p1)
        i2 = find_index(p2)
        if i1 != -1 and i2 != -1:
            edges.append((i1, i2))
            edges.append((i2, i1))

# Saída: imprimir o grafo
print("Nós válidos:")
for i, n in enumerate(nodes):
    print(f"{i}: {n}")

print("\nArestas do grafo:")
for e in edges:
    print(e)
