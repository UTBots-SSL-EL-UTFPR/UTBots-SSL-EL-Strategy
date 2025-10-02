"""_summary_: Para usar, é precisO chamar a função is_visible e passar os argumentos:
* Uma matriz com as posições de cada obstáculo
* Uma tupla com com as posições (x, y) do chutador
* Componente x do gol
"""
import math
from utils.pose2D import Pose2D
from utils.defines import (ROBOT_RADIUS)
from .field_helper import (GOAL_LENGHT)
from utils.defines import (ROBOT_RADIUS)
from .field_helper import (GOAL_LENGHT)


"""_summary_: Classe dos obstáculos, que guarda suas posições (x, y) e os
ângulos das suas retas tangentes que passam por (x0, y0)
"""
class Obstacle:
   def __init__(self, xr, yr, theta_bottom=-1, theta_top=-1):
       self.xr = xr
       self.yr = yr
       self.theta_bottom = theta_bottom
       self.theta_top = theta_top


"""_summary_: Combina as expressões (x=x0+cos(angulo), y=y0+sen(angulo)) com
(x+x0)²+(y+y0)²=ROBOT_RADIUS² para verificar se a reta cruza o bob


   return _type_: bool
"""
def haIntersecao(xr, yr, x0, y0, angulo):
   a = 1
   b = 2 * (math.cos(angulo) * (x0 - xr) + math.sin(angulo) * (y0 - yr))
   c = (x0 - xr) ** 2 + (y0 - yr) ** 2 - ROBOT_RADIUS**2
   delta = (
       b**2 - 4 * a * c
   )
   if delta >= 0:
       return True
   return False


"""_summary_: Calcula os ângulos das retas tangentes que passam por (x0, y0) de
cada um dos bobs visíveis. Combina y = y0 + m(x-x0) com R = |axr + bxr + c|/(sqrt(a²+b²))
(distância entre um ponto e uma reta). Quando x_gol<0, descobre o ângulo sabendo
o ângulo oposto pelo vértice


return _type_: tupla
"""
def ang_tangent_lines(x0, y0, xr, yr, x_gol):
   a = ROBOT_RADIUS**2 - (xr - x0) ** 2
   b = -2 * (xr - x0) * (y0 - yr)
   c = -((y0 - yr) ** 2) + ROBOT_RADIUS**2
   delta = b**2 - 4 * a * c
   if delta >= 0:
       m1 = (-b + math.sqrt(delta)) / (2 * a)
       m2 = (-b - math.sqrt(delta)) / (2 * a)
       theta1 = math.atan(m1)
       theta2 = math.atan(m2)
       if x_gol < 0:
           tmp = theta1
           theta1 = -1 * theta2
           theta2 = -1 * tmp
       theta1 = min(theta1, theta2)
       theta2 = max(theta1, theta2)
       return theta1, theta2
  
"""_summary_: Cria uma lista com os obstáculos que estão entre as retas que partem de (x0, y0)
e terminam nos limites do gol. Para tanto, verifica se essas retas cortam algum bob ou se as retas
que partem de (x0, y0) e passam por (xr, yr) cruzam o gol.


return _type_: list
"""
def calc_visible_bobs(
   x0, y0, obstacles_coord, goal_pose, theta_max, theta_min
):
   x_gol = gol_center.x
   y_golMax =  gol_center.y + GOAL_LENGHT / 2
   y_golMin =  gol_center.y - GOAL_LENGHT / 2
   visible_bobs = []
   for i in range(len(obstacles_coord)):
       xr = obstacles_coord[i].x
       yr = obstacles_coord[i].y
       if (x_gol > 0 and xr < 0) or (x_gol < 0 and xr > 0) or (xr == x0):
           continue
       m = (yr - y0) / (xr - x0)
       intersec_y = m * (x_gol - x0) + y0
       if (intersec_y >= y_golMin and intersec_y <= y_golMax) or (
           haIntersecao(xr, yr, x0, y0, theta_min)
           or haIntersecao(xr, yr, x0, y0, theta_max)
       ):
           tangent_angles = ang_tangent_lines(x0, y0, xr, yr, x_gol)  # type: ignore
           if tangent_angles is None:
               continue
           theta_bottom, theta_top = tangent_angles
           bob = Obstacle(xr, yr, theta_bottom, theta_top)  # type: ignore
           visible_bobs.append(bob)


   return visible_bobs


"""_summary_: Remove da lista dos robôs visíveis aqueles cujas tangentes estão entre as tangentes dos
demais obstáculos


return _type_: void (altera a lista passada como parâmetro)
"""
def removePontosCegos(visible_bobs):
   to_remove = []
   for bob in visible_bobs:
       for i in range(len(visible_bobs)):
           obs = visible_bobs[i]
           if (
               bob.theta_top < obs.theta_top and bob.theta_top > obs.theta_bottom
           ) and (
               bob.theta_bottom < obs.theta_top and bob.theta_bottom > obs.theta_bottom
           ):
               to_remove.append(bob)
   for i in range(len(to_remove)):
       visible_bobs.remove(to_remove[i])


"""_summary_: Identifica o maior ângulo da visão do gol. Primeiramente, calcula os obstáculos visíveis, remove
aqueles entre pontos cegos e organiza eles segundo o ângulo da tangente inferior. Depois, itera entre a tangente
superior de um obstáculo até a tangente superior do próximo.


return _type_: float (módulo do ângulo em graus)
"""
def limits_of_visibility(obstacles: list[Pose2D], p0: Pose2D, gol_center: Pose2D) -> list[float]:
   x_gol = gol_center.x
   y_golMax =  gol_center.y + GOAL_LENGHT / 2
   y_golMin =  gol_center.y - GOAL_LENGHT / 2
   x0 = p0.x
   y0 = p0.y
   

   kick_angle = [0, 0]
   if x_gol == x0:
       return kick_angle


   theta_max = math.atan((y_golMax - y0) / ((x_gol - x0)))
   theta_min = math.atan((y_golMin - y0) / ((x_gol - x0)))
   if x_gol < 0:
       theta_min *= -1
       theta_max *= -1
   theta = theta_min


   visible_bobs = calc_visible_bobs(
       x0, y0, obstacles, gol_center, theta_max, theta_min
   )
   removePontosCegos(visible_bobs)
   visible_bobs.sort(
       key=lambda bob: bob.theta_bottom
   )


   if not visible_bobs:
       kick_angle = [theta, theta_max]
   else:
       for i in range(len(visible_bobs)):
           theta_bottom = visible_bobs[i].theta_bottom
           theta_top = visible_bobs[i].theta_top
           intervalo = theta_bottom - theta
           if intervalo >= 0 and intervalo > (kick_angle[1] - kick_angle[0]):
               kick_angle = [theta, theta_bottom]
           theta = theta_top
           if theta >= theta_max:
               break
           elif (i == len(visible_bobs) - 1) and theta < theta_max:
               if theta_max - theta > kick_angle[1] - kick_angle[0]:
                   kick_angle = [theta, theta_max]
   return kick_angle


def max_range_of_visibility(obstacles: list[Pose2D], p0: Pose2D, gol_center: Pose2D) -> float:
   kick_angle = limits_of_visibility(obstacles, p0, gol_center)
   return abs(kick_angle[1] - kick_angle[0])

# Teste


if __name__ == "__main__":
    obstacles = [(Pose2D)(600, 0), (Pose2D)(1600, 100), (Pose2D)(-1000, 0), (Pose2D)(1400, -200)]
    obstacles = [(1400, 100)]
    p0 = (Pose2D)(0,0)
    gol_center = (Pose2D)(2250, 0)
    inicio, fim = limits_of_visibility(obstacles, p0, gol_center)
    print(math.degrees(inicio))
    print(math.degrees(fim))
    angle = (limits_of_visibility(obstacles, p0, gol_center))
    print(angle)