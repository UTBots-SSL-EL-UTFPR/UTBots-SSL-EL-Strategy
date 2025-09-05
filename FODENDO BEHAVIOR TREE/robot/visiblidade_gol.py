import math

ROBOT_RADIUS = 85   # está em mm

def haIntersecao (xr, yr, x0, y0, angulo):
    a = 1
    b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)*(y0-yr))
    c = (x0 - xr)**2 + (y0-yr)**2 - ROBOT_RADIUS**2
    delta = b**2 - 4*a*c # Se o delta for negativo, a reta não cruza a circunferência
    if (delta >= 0):
        t1 = (-b + math.sqrt(delta)) / (2*a)
        t2 = (-b - math.sqrt(delta)) / (2*a)
        if (t1 >= 0 or t2>=0):
            return True
    return False

# Calcua
def calc_visible_bobs(x0, y0, obstacles, x_gol, y_golMin, y_golMax, theta_max, theta_min):
    visible_bobs = []
    for i in range(len(obstacles)):
        xr = obstacles[i][0]
        yr = obstacles[i][1]
        if((x_gol > 0 and xr < 0) or (x_gol < 0 and xr > 0)):
            continue
        m = (yr-y0) / (xr-x0)
        intersec_y = m(x_gol - x0) + y0
        if (intersec_y >= y_golMin or intersec_y <= y_golMax):
            visible_bobs.insert((xr, yr))
        elif (haIntersecao(xr, yr, x0, y0, theta_min) or haIntersecao(xr, yr, x0, y0, theta_max)):
              visible_bobs.insert((xr, yr))
    return visible_bobs

# calcula o ângulo das retas tangentes à circunferência
def ang_tangent_lines(x0, y0, xr, yr, theta):
    a = ROBOT_RADIUS**2 - (xr-x0)**2
    b = -2*(xr-y0)*(y0-yr)
    c = -(y0-yr)**2 + ROBOT_RADIUS**2
    delta = b**2 - 4*a*c # Se o delta for negativo, (x0, y0) estão dentro do bob
    if (delta >= 0):
        m1 = (-b + math.sqrt(delta)) / (2*a)
        m2 = (-b - math.sqrt(delta)) / (2*a)
        theta1 = math.atan(m1) - theta
        theta2 = math.atan(m2) - theta
        return (min(theta1, theta2), max(theta, theta2))
    # Preciso retornar algo em caso de erro ou o Phyton faz isso por mim?

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
    
    visible_bobs = calc_visible_bobs(x0, y0, obstacles, x_gol, y_golMin, y_golMax, theta_max, theta_min)

# Teste
if __name__ == "__main__":
    obstacles = [(1000, 0), (-1600, -500)]
    p0 = (0,0)
    x_gol = 2250
    y_golMax = 750
    y_golMin = -750

    inicio, fim = (is_visible(obstacles, p0, x_gol, y_golMin, y_golMax))
    print(math.degrees(inicio))
    print(math.degrees(fim))