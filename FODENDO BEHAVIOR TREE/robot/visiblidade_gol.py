import math
ROBOT_RADIUS = 85   # está em mm

class Obstacle:
    def __init__(self, xr, yr , theta_bottom = -1, theta_top = -1):
        self.xr = xr
        self.yr = yr
        # Ângulos das retas tangentes ao bob e que passam por (x0, y0)
        self.theta_bottom = theta_bottom    
        self.theta_top = theta_top

# Estou apenas reutilizando uma função que eu fiz em ray_casting
def haIntersecao (xr, yr, x0, y0, angulo):
    a = 1
    b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)*(y0-yr))
    c = (x0 - xr)**2 + (y0-yr)**2 - ROBOT_RADIUS**2
    delta = b**2 - 4*a*c # Se o delta for negativo, a reta não cruza a circunferência
    if (delta >= 0):
        return True
    return False

# Calcula o ângulo das retas tangentes à circunferência
def ang_tangent_lines(x0, y0, xr, yr, x_gol):
    a = ROBOT_RADIUS**2 - (xr-x0)**2
    b = -2*(xr-x0)*(y0-yr)
    c = -(y0-yr)**2 + ROBOT_RADIUS**2
    delta = b**2 - 4*a*c # Se o delta for negativo, (x0, y0) estão dentro do bob
    if (delta >= 0):
        m1 = (-b + math.sqrt(delta)) / (2*a)
        m2 = (-b - math.sqrt(delta)) / (2*a)
        theta1 = math.atan(m1)
        theta2 = math.atan(m2)
        if(x_gol<0):
            # Muda o ângulo para o 3º e o 4º quadrante
            tmp = theta1
            theta1 = -1 * theta2
            theta2 = -1 * tmp
        theta1 = (min(theta1, theta2))
        theta2 = (max(theta1, theta2))
        return theta1, theta2

# Calcua ums lista com os obstáculos que estão no campo de visão do chutador
def calc_visible_bobs(x0, y0, obstacles_coord, x_gol, y_golMin, y_golMax, theta_max, theta_min):
    visible_bobs = []
    for i in range(len(obstacles_coord)):
        xr = obstacles_coord[i][0]
        yr = obstacles_coord[i][1]
        # Se o obstáculo está atrás do robô, nem faz conta com ele e já descarta
        if((x_gol > 0 and xr < 0) or (x_gol < 0 and xr > 0) or (xr==x0)):
            continue
        # Vê se a reta que passa pelo chutador e  o centro do obstáculo cruza o gol ou
        # se uma das retas que passam pelo limite do gol e o centro do chutador cruza o obstáculo 
        m = (yr-y0) / (xr-x0)
        intersec_y = m*(x_gol - x0) + y0
        if ((intersec_y >= y_golMin and intersec_y <= y_golMax)
            or (haIntersecao(xr, yr, x0, y0, theta_min) or haIntersecao(xr, yr, x0, y0, theta_max))):
            theta_bottom, theta_top = ang_tangent_lines(x0, y0, xr, yr, x_gol)
            bob = Obstacle(xr, yr, theta_bottom, theta_top)
            visible_bobs.append(bob)
        
    return visible_bobs

# Remove da lista aqueles obstáculos cuja tangente está entre as tangentes de outros obstáculos
def removePontosCegos(visible_bobs):
    to_remove = []
    for bob in visible_bobs:
        for i in range(len(visible_bobs)):
            obs = visible_bobs[i]
            if ((bob.theta_top < obs.theta_top and bob.theta_top > obs.theta_bottom)
                and (bob.theta_bottom < obs.theta_top and bob.theta_bottom > obs.theta_bottom)):
                to_remove.append(bob)
    for i in range(len(to_remove)):
        visible_bobs.remove(to_remove[i])

# Retorna o maior intervalo de visão
def is_visible(obstacles, p0, x_gol, y_golMin, y_golMax):
    x0 = p0[0]    # Posição do robô  que está chutando
    y0 = p0[1]

    # Ângulo entre os lims. do gol e o chutador
    theta_max = math.atan((y_golMax - y0)/((x_gol - x0)))
    theta_min = math.atan((y_golMin - y0)/((x_gol - x0)))
    if(x_gol<0):
        theta_min*=-1
        theta_max*=-1
    theta = theta_min
    kick_angle = [0,0]  # Lista com o início e o fim do intervalo de visão
    
    visible_bobs = calc_visible_bobs(x0, y0, obstacles, x_gol, y_golMin, y_golMax, theta_max, theta_min)
    removePontosCegos(visible_bobs)
    visible_bobs.sort(key=lambda bob: bob.theta_bottom) # Organiza a lista em ordem crescente do ângulo da reta tangência à parte inferior do bob

    # Se não há obstáculos no campo de visão, já retorna os ângulos entre as retas limites do gol
    if(not visible_bobs):
        kick_angle = [theta, theta_max]
    else:
        # Varre o ângulo entre a parte de cima de um bob e a parte de baixo de outro (armazena o maior intervalo)
        for i in range(len(visible_bobs)):
            theta_bottom = visible_bobs[i].theta_bottom
            theta_top = visible_bobs[i].theta_top
            intervalo = theta_bottom - theta
            if(intervalo >=0 and intervalo > (kick_angle[1] - kick_angle[0])):
                kick_angle = [theta, theta_bottom]
            theta = theta_top
            if(theta >= theta_max):
                break
            elif((i == len(visible_bobs)-1) and theta < theta_max):
                if(theta_max - theta > kick_angle[1] - kick_angle[0]):
                    kick_angle = [theta, theta_max] 
    # Retorna o módulo para que não haja distinção entre x_gol>0 e x_gol<0
    return math.fabs(math.degrees(kick_angle[1]-kick_angle[0]))
'''
#Teste
if __name__ == "__main__":
    obstacles = [(1400, 100), (1200, -400), (2000,700), (1700, 0)]
    p0 = (1000, 500)
    x_gol = 2250
    y_golMax = 750
    y_golMin = -750

    angle = (is_visible(obstacles, p0, x_gol, y_golMin, y_golMax))
    print(angle)
'''