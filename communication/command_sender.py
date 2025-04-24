import socket
from communication.generated import grSim_Commands_pb2
class CommandSender:
    def __init__(self, ip: str = "127.0.0.1", port: int = 20011):
        self.address = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_command(self, commands: list[dict]): #recebe uma lista de dicionários com comandos para cada robô
        """
        Envia uma lista de comandos (um por robô) para o simulador.

        Parameters:
            commands (list of dict): Cada dicionário deve conter as chaves:
                - id (int): ID do robô
                - team (str): 'blue' ou 'yellow'
                - wheel_speeds (list of float): velocidades das rodas
                - kick_speed (float): velocidade de chute
                - dribbler_speed (float): velocidade do dribbler
        """
        packet = self._build_packet(commands)
        self.socket.sendto(packet.SerializeToString(), self.address)

    def _build_packet(self, commands: list[dict]) -> grSim_Commands_pb2.grSim_Packet: #constroi uma mensagem protobuf com base nos comandos fornecidos
        packet = grSim_Commands_pb2.grSim_Packet()
        packet.commands.timestamp = 0  # pode ser usado depois
        packet.commands.isteamyellow = (commands[0]['team'].lower() == 'yellow')

        for cmd in commands:
            robot_cmd = packet.commands.robot_commands.add()
            robot_cmd.id = cmd['id']
            robot_cmd.wheelsspeed = True  # usamos velocidades por roda
            robot_cmd.wheel1 = cmd['wheel_speeds'][0]
            robot_cmd.wheel2 = cmd['wheel_speeds'][1]
            robot_cmd.wheel3 = cmd['wheel_speeds'][2]
            robot_cmd.wheel4 = cmd['wheel_speeds'][3]
            robot_cmd.kickspeedx = cmd.get('kick_speed', 0.0)
            robot_cmd.spinner = cmd.get('dribbler_speed', 0.0) > 0

        return packet
    
