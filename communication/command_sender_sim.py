import socket

class CommandSenderSim:
    _instance = None

    def __new__(cls, ip: str = "127.0.0.1", port: int = 20011): #singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ip: str = "127.0.0.1", port: int = 20011):
        if self._initialized:
            return
        self.address = (ip, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #inicializa um socket  
        self._initialized = True

    def send(self, packet_bytes: bytes):       #envia o pacote dado no endereço dado
        self.sock.sendto(packet_bytes, self.address)
