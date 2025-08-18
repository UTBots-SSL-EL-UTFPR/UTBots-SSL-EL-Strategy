import threading
import socket
from communication.receiver.receiver import Receiver
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb
from communication.parsers import RefereeParser
from SSL_configuration.configuration import Configuration
class RefereeReceiver(Receiver):
    _instance = None

    def __new__(cls, *args, **kwargs):  # singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "sock"): 
            return
        config = Configuration.getObject()
        super().__init__(multicast_ip=config.referee_receiver_ip, port=config.referee, interface_ip=config.interface_ip_referee)
        self.latest_raw = None #guarda o ultimo pacote bruto recebido
        self.latest_parsed = None #guarda o ultimo objeto protobuf decodificado
        self.parser = RefereeParser()

        self._thread = threading.Thread(target=self.receive_raw, daemon=True) # thread que escuta pacotes em segundo plano
        self._thread.name = "RefereeReceiverThread"
        self._thread.daemon = True  # permite que o programa termine mesmo com a thread rodando
        self._thread.start()

    def receive_raw(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(65535)
                self.latest_raw = data #salva o pacote bruto recebido                                                                                                                                                                                                                                                                                                 
                self.latest_parsed = self.parser.parse(data) #usa o parser para decodificar os bytes do pacote em um objeto pyhton com campos acessiveis
            except Exception as e:
                print(f"[RefereeReceiver] Erro ao receber pacote: {e}")

    #2 gets para retornar os dados mais recentes
    def get_latest_raw(self):
        return self.latest_raw

    def get_latest_parsed(self):
        return self.latest_parsed
