import time
from communication.command_builder import CommandBuilder
from communication.command_sender_sim import CommandSenderSim

builder = CommandBuilder(team_color="blue")

builder.add_command(
    id=0,
    vx=10.0,    # velocidade tangencial (eixo X) em m/s
    vy=0.0,     # velocidade normal (eixo Y) em m/s
    w=0.0,      # velocidade angular (rad/s)
    kick_x=0.0,
    kick_z=0.0,
    spinner=False
)

sender = CommandSenderSim()

start_time = time.time()

while time.time() - start_time < 1.0:
    packet_bytes = builder.build()
    sender.send(packet_bytes)
    time.sleep(0.016)  # ~60 pacotes por segundo
