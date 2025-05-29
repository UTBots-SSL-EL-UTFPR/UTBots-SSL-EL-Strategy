from abc import ABC, abstractmethod
import socket

class Receiver(ABC):    #classe base que configura o socket UDP generico
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock = self._create_socket()

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #cria um novo socket de rede
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #define o tipo de endereço (IPv4) e o tipo de protocolo (UDP)
        sock.bind((self.ip, self.port))                             #socket começa a escutar no IP e na porta fornecidos
        return sock

    @abstractmethod
    def receive(self):
        #função virtual pura
        pass