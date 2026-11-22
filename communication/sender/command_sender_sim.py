import socket


class CommandSenderSim:
    """Envia o pacote do grSim para o simulador e/ou para os robôs físicos.

    O destino vem de configuration.json -> "Robot_real" -> "mode":
        "sim"  - só o grSim (padrão)
        "real" - só os robôs físicos (protocolo do firmware, ver command_sender_robot.py)
        "both" - os dois: o robô físico repete o que o robô do simulador faz
    """

    _instance = None

    def __new__(cls, ip: str = "127.0.0.1", port: int = 20011):  # singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ip: str = "127.0.0.1", port: int = 20011):
        if self._initialized:
            return
        self.address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # inicializa um socket
        self.to_sim, self.robot_sender = True, None
        self._setup_robot_sender()
        self._initialized = True

    def _setup_robot_sender(self):
        from SSL_configuration.configuration import Configuration

        settings = Configuration.getObject().robot_real or {}
        mode = settings.get("mode", "sim")
        if mode not in ("sim", "real", "both"):
            raise ValueError(f'Robot_real.mode inválido: "{mode}" (use sim, real ou both)')
        self.to_sim = mode in ("sim", "both")
        if mode in ("real", "both"):
            from communication.sender.command_sender_robot import CommandSenderRobot

            self.robot_sender = CommandSenderRobot(settings)

    def send(self, packet_bytes: bytes):  # envia o pacote dado no endereço dado
        if self.to_sim:
            self.sock.sendto(packet_bytes, self.address)
        if self.robot_sender is not None:
            self.robot_sender.send(packet_bytes)
