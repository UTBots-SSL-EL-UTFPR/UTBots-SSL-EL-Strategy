'''
FEITO NO ÚLTIMO DIA: testes das velocidades linear e angular (estão funcioando)
AINDA FALTA: arrumar a orientação de {b}
'''

import time
import numpy as np
import math
from communication.command_builder import CommandBuilder
from communication.command_sender_sim import CommandSenderSim

'''
{w} = referencial da roda
{b} = referencial do robô
{s} = referencial do mundo
'''

wheels_angles = [math.radians(150), # Ângulos das rodas a partir de y-
                 math.radians(-135),
                 math.radians(-45),
                 math.radians(30)]
gamma = [0, 0, 0, 0]
wheel_radius = 0.027
robot_radius = 0.09
nrodas = 4

def motorVel (q, coord, phi):
    h = np.zeros((nrodas, 3))
    for i in range(nrodas):
        xi, yi = coord[i]
        Bi = wheels_angles[i]   # Ângulo entre {w} e {b}
        gammai = gamma[i]
        hi = np.array([robot_radius,
                       np.cos(Bi+phi+gammai),
                       np.sin(Bi+phi+gammai)])
        hi /= (wheel_radius*np.cos(gammai))  # Operações compactadas
        h[i][0] = hi[0]
        h[i][1] = hi[1]
        h[i][2] = hi[2]
    u = h @ q
    return u

if __name__ == "__main__":
    w = 0
    vx = 0
    vy = 0
    q = np.array([[w], [vx], [vy]]) # Velocidade do robô em {s}
    phi = math.radians(0)   # Ângulo entre {s} e {b}
    coord = []  # (x, y) de cada roda
    for i in range(nrodas):
        gammai = gamma[i]
        Bi = wheels_angles[i]
        coord.append((robot_radius*np.cos(Bi), robot_radius*np.sin(Bi)))

    u = motorVel(q, coord, phi)
    builder = CommandBuilder(team_color="blue")
    builder.command_robots(
        id = 0,
        wheelsspeed= True,
        wheel1= u[0].item(),
        wheel2= u[1].item(),
        wheel3= u[2].item(),
        wheel4= u[3].item(),
    )

    sender = CommandSenderSim()
    start_time = time.time()
    while time.time() - start_time < 3.0:
        packet_bytes = builder.build()
        sender.send(packet_bytes)
        time.sleep(0.016)  # ~60 pacotes por segundo