from communication.receiver import Receiver
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb
from communication.parsers import RefereeParser
import socket

class RefereeReceiver(Receiver):
    _instance = None 

    def __new__(cls,*args, **kwargs):                             #singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # cria uma nova instância
        return cls._instance    # Isso é útil para evitar múltiplos sockets escutando a mesma porta multicast ao mesmo tempo, o que poderia causar erros.

    def __init__(self, interface_ip: str):
        if not hasattr(self, "sock"):   #Só cria o socket se ele ainda não existe
            super().__init__(multicast_ip="224.5.23.1", port=10003, interface_ip=interface_ip) #Configura o IP do grupo Multicast( do Game Controller) e a porta, além do IP do docker

    def receive_raw(self):  # Espera e recebe pacotes brutos UDP do Game Controller
        #print("Aguardando pacote bruto do Game Controller...")
        self.sock.settimeout(5)  # Definindo um tempo limite de 5 segundos para esperar os dados
        try:
            data, _ = self.sock.recvfrom(65535) # Recebe os dados brutos
            #print(f"Pacote bruto recebido com {len(data)} bytes.")
            return data
        except socket.timeout: #Mensagem para quando falhar ao receber os dados
            print("Timeout: Nenhum pacote recebido.")
            return None
        
    def receive_parsed(self):
        raw_data = self.receive_raw()
        if raw_data:
            parser = RefereeParser()
            return parser.parse(raw_data)
        return None