import time
from communication.command_builder import CommandBuilder
from communication.command_sender_sim import CommandSenderSim

builder = CommandBuilder(team_color="blue")
sender = CommandSenderSim()

builder.replace_robots(
        x = 0.0,
        y = 1.0,
        dir = 0.0,
        id = 1,
        yellowTeam = False,
        turnon = True
    )

packet_bytes = builder.build()
sender.send(packet_bytes)


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

packet_bytes = builder.build()
sender.send(packet_bytes)