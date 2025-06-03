import sys
sys.path.append('/home/futebol_de_robos/FutebolDeRobos/UTBots-SSL-EL-Strategy')
from communication.receiver import Receiver
from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.parsers import VisionParser
import socket

class VisionReceiver(Receiver):
    _instance = None 

    def __new__(cls,*args, **kwargs):                             #singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # cria uma nova instância
        return cls._instance    # Isso é útil para evitar múltiplos sockets escutando a mesma porta multicast ao mesmo tempo, o que poderia causar erros.

    def __init__(self, interface_ip: str):
        if not hasattr(self, "sock"):   #Só cria o socket se ele ainda não existe
            super().__init__(multicast_ip="224.5.23.2", port=10020, interface_ip=interface_ip) #Configura o IP do grupo Multicast(do SSL Vision) e a porta, além da interface

    def receive_raw(self):  # Espera e recebe pacotes brutos UDP do SSL-vision/GrSim
        #print("Aguardando pacote bruto do SSL vision...")
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
            parser = VisionParser()
            return parser.parse(raw_data)
        return None