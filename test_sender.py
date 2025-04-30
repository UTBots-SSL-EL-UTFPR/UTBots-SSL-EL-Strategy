import time
from communication.command_builder import CommandBuilder
from communication.command_sender_sim import CommandSenderSim

builder = CommandBuilder(team_color="blue")

builder.command_robots(
    id=0,
    vx=10.0,    
    vy=0.0,     
    w=0.0,      
    kick_x=5.0,
    kick_z=5.0,
    spinner=False
)

builder.command_robots(
    id=2,
    vx=10.0,   
    vy=0.0,     
    w=0.0,      
    kick_x=5.0,
    kick_z=5.0,
    spinner=False
)


sender = CommandSenderSim()

start_time = time.time()

while time.time() - start_time < 1.0:
    packet_bytes = builder.build()
    sender.send(packet_bytes)
    time.sleep(0.016)  # ~60 pacotes por segundo

builder.replace_ball(
    x = 1.0,
    y = 1.5,
    vx= 0.0,
    vy = 0.0
)

builder.replace_robots(
    x = 1.00,
    y = 1.00,
    dir = 0.0,
    id = 3,
    yellowTeam = False,
    turnon = True
)

builder.replace_robots(
    x = -1.00,
    y = 1.00,
    dir = 1.0,
    id = 1,
    yellowTeam = True,
    turnon = False
)

packet_bytes = builder.build()
sender.send(packet_bytes)