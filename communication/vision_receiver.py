import threading
import socket
from communication.receiver import Receiver
from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.parsers import VisionParser

class VisionReceiver(Receiver):
    _instance = None

    def __new__(cls, *args, **kwargs):  # singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, interface_ip: str,ip:str,portVision:int):

        if not hasattr(self, "sock"):  # só inicializa uma vez
            super().__init__(multicast_ip=ip, port=portVision, interface_ip=interface_ip)
            self.latest_raw = None #guarda o ultimo pacote bruto recebido
            self.latest_parsed = None #guarda o ultimo objeto protobuf decodificado
            self.parser = VisionParser()

            self._thread = threading.Thread(target=self.receive_raw, daemon=True)
            self._thread.name = "VisionReceiverThread"
            self._thread.daemon = True  # permite que o programa termine mesmo com a thread rodando
            self._thread.start()

            self.isSimulation = True


    def receive_raw(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(65535)
                self.latest_raw = data # salva o pacote bruto recebido
                self.latest_parsed = self.parser.parse(data) # usa o parser para decodificar os bytes do pacote em um objeto python com campos acessíveis
            except Exception as e:
                print(f"[VisionReceiver] Erro ao receber pacote: {e}")


    # 2 gets para retornar os dados mais recentes
    def get_latest_raw(self):
        return self.latest_raw

    def get_latest_parsed(self):
        return self.latest_parsed
