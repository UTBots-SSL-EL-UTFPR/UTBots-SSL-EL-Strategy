# command_sender_real.py
import socket
from typing import Dict, Tuple
from communication.sender.messages import Movement, MSG_ID_PING

class CommandSenderReal:
    """
    Envia pacotes UDP para robôs reais.
    """
    def __init__(self, local_bind_ip: str = '0.0.0.0'):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind opcional (porta efêmera); útil para estabilizar rota/firewall
        self.sock.bind((local_bind_ip, 0))
        self.robot_endpoints: Dict[int, Tuple[str, int]] = {}  # id -> (ip, port)

    def register_robot(self, robot_id: int, ip: str, port: int):
        self.robot_endpoints[robot_id] = (ip, port)

    def send(self, movement: Movement) -> bool:
        endpoint = self.robot_endpoints.get(movement.robot_id)
        if not endpoint:
            return False
        try:
            self.sock.sendto(movement.pack(), endpoint)
            return True
        except OSError:
            return False

    def send_ping(self, robot_id: int) -> bool:
        endpoint = self.robot_endpoints.get(robot_id)
        if not endpoint:
            return False
        ping = Movement(message_id=MSG_ID_PING, robot_id=robot_id,
                        v1=0, v2=0, v3=0, v4=0, kicker=False)
        try:
            self.sock.sendto(ping.pack(), endpoint)
            return True
        except OSError:
            return False
