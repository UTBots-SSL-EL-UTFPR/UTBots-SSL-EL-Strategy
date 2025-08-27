import math
from utils import pose2D    # Não tenho certeza de como faz o import

ROBOT_RADIUS = 0.09

def haIntersecao (xr, yr, x0, y0, angulo):
    a = 1
    b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)*(y0-yr))
    c = (x0 - xr)**2 + (y0-yr)**2 - ROBOT_RADIUS**2
    delta = b**2 - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo
    if (delta >= 0):
        t1 = (-b + math.sqrt(delta)) / (2*a)
        t2 = (-b - math.sqrt(delta)) / (2*a)
        if (t1 >= 0):
            return t1
        elif (t2>=0):
            return t2
    return 0

def skip_bob(theta, x, y):
    phi = theta + math.pi/2 # Ângulo entre x+ e a reta perpendicular ao raio
    t = haIntersecao(x, y, x, y, phi)
    x_prox = x + t*math.cos(phi)
    theta = math.cos(x_prox/t)
    return theta

def is_visible(obstacles: list[Pose2D], p0: *Pose2D, x_gol: int, y_golMin: int, y_golMax):
    x = p0.x
    y = p0.y
    # Ângulo entre os lims. do gol e o bob chutando
    theta_max = math.atan((y_golMax - y)/((x_gol - x)))
    theta_min = math.atan((y_golMin - y)/((x_gol - x))) 
    delta_theta = math.pi/180   # Cada raio é lançado a cada ~1 grau
    theta = theta_min
    angulo_chute_aux = [0, 0]
    angulo_chute = [0,0]

    vision = False
    # A cada d(theta), verifica se o raio bate no gol
    while (theta <= theta_max):
        find_goal = True
        for i in range(len(obstacles)):
            if(haIntersecao(obstacles[i].x, obstacles[i].y, x, y, theta)):
                find_goal = False
                skip_bob(theta, x, y)
                break
        if(find_goal):
            if(not vision):
                angulo_chute_aux[0] = theta
                vision = True
            else:
                angulo_chute_aux[1] = theta
        else:
            if(vision):
                if(angulo_chute[1]-angulo_chute[0] < angulo_chute_aux[1]-angulo_chute_aux[0]):
                    angulo_chute[0] = angulo_chute_aux[0]
                    angulo_chute[1] = angulo_chute_aux[1]
                    angulo_chute_aux = [0,0]
        theta += delta_theta
    return False
        