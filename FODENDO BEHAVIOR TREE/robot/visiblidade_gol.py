import math

ROBOT_RADIUS = 90   # está em mm

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

# calcula o ângulo entre a origem e o último ponto (na vertical) da circunferência
def skip_bob(theta, xr, yr, x0):
    phi = theta + math.pi/2 # Ângulo entre x+ e a reta perpendicular ao raio
    t = haIntersecao(xr, yr, xr, yr, phi)   # Encontra o praâmetro e calcula o ângulo
    x_prox = xr + t*math.cos(phi)   # x do limite superior da circunferência
    theta = math.cos((x_prox-x0)/t)
    return theta

# retorna o maior intervalo de visão
def is_visible(obstacles, p0, x_gol, y_golMin, y_golMax):
    x0 = p0[0]    # Posição dop robô  que está chutando
    y0 = p0[1]
    d = math.sqrt(y0**2 + (x_gol-x0)**2) # Distância em relação ao meio do gol

    # Ângulo entre os lims. do gol e o bob chutando
    theta_max = math.atan((y_golMax - y0)/((x_gol - x0)))
    theta_min = math.atan((y_golMin - y0)/((x_gol - x0))) 
    delta_theta = (theta_max - theta_min)/d    # O n° de raios lançados é igual à distância (em mm) do gol
    theta = theta_min

    angulo_chute_aux = [-1, -1]
    angulo_chute = [-1,-1]  # Lista com o início e o fim do intervalo de visão
    vision = False 

    while (theta <= theta_max):
        find_goal = True
        # Verifica se há intercecção em cada obstáculo 
        for i in range(len(obstacles)):
            if(haIntersecao(obstacles[i][0], obstacles[i][1], x0, y0, theta)):
                find_goal = False
                skip_bob(theta, obstacles[i][0], obstacles[i][1], x0)
                break
        if(find_goal):
            if(not vision):
                angulo_chute_aux[0] = theta
                vision = True
        else:
            if(vision):
                angulo_chute_aux[1] = theta
                vision = False
                if(angulo_chute[1]-angulo_chute[0] < angulo_chute_aux[1]-angulo_chute_aux[0]):
                    angulo_chute[0] = angulo_chute_aux[0]
                    angulo_chute[1] = angulo_chute_aux[1]
                angulo_chute_aux = [-1,-1]
        theta += delta_theta
    return angulo_chute # retorna o maior ângulo de visão, senão retorna [-1,-1]

# Teste
if __name__ == "__main__":
    obstacles = [[1000, 0]]
    p0 = [0,0]
    x_gol = 2250
    y_golMax = 750
    y_golMin = -750

    inicio, fim = (is_visible(obstacles, p0, x_gol, y_golMin, y_golMax))
    print(math.degrees(inicio))
    print(math.degrees(fim))