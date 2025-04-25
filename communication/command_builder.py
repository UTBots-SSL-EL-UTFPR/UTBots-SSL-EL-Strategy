from communication.generated import grSim_Packet_pb2
import time

class CommandBuilder:
    def __init__(self, team_color: str = "blue"):
        self.packet = grSim_Packet_pb2.grSim_Packet()   # cria o pacote de comandos grSim
        self.packet.commands.isteamyellow = (team_color == "yellow")

    def add_command(self, id: int, vx: float, vy: float, w: float,
                    kick_x: float = 0.0, kick_z: float = 0.0,
                    spinner: bool = False):
        cmd = self.packet.commands.robot_commands.add() # adiciona um comando de robô
        cmd.id = id
        cmd.velnormal = vy
        cmd.veltangent = vx
        cmd.velangular = w
        cmd.kickspeedx = kick_x
        cmd.kickspeedz = kick_z
        cmd.spinner = spinner
        cmd.wheelsspeed = False  

    def build(self) -> bytes:
        self.packet.commands.timestamp = time.time()    # preenche o campo obrigatório 'timestamp'
        return self.packet.SerializeToString()
