from abc import ABC, abstractmethod # permite que a classe seja marcada como abstrata (não instanciável diretamente)
import struct # permite empacotar dados binários, usado aqui para configurar o multicast.
import socket

class Receiver(ABC):    #classe base que configura o socket UDP generico
    def __init__(self, multicast_ip, port, interface_ip): #argumentos considerando o docker por interface ip
        self.multicast_ip = multicast_ip
        self.port = port
        self.interface_ip = interface_ip
        self.sock = self._create_socket()

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #cria um novo socket de rede
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #define o tipo de endereço (IPv4) e o tipo de protocolo (UDP)
        sock.bind(('', self.port))                             #socket começa a escutar no IP e na porta fornecidos

        # Criação da estrutura binária mreq exigida pela opção IP_ADD_MEMBERSHIP
        mreq = struct.pack("=4s4s", socket.inet_aton(self.multicast_ip), socket.inet_aton(self.interface_ip)) #inet_aton() converte um endereço IP para o formato binário necessário.
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # Adiciona o socket ao grupo multicast definido em mreq, permitindo que ele receba os pacotes enviados ao grupo.

        return sock

    @abstractmethod     #Implementa o método abstrato usado pelas derivadas
    def receive_raw(self):
        #função virtual pura
        pass