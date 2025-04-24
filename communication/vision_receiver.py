from communication import Receiver
from communication.generated import ssl_vision_wrapper_pb2 as vision_pb

class VisionReceiver(Receiver):
    _instance = None 

    def __new__(cls):                             #singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # cria uma nova instância
        return cls._instance

    def __init__(self):
        if not hasattr(self, "sock"):
            super().__init__(ip="0.0.0.0", port=10020) #TODO, coloquei qualquer valor aqui pro ip e port

    def receive(self):
        data, _ = self.sock.recvfrom(65535)     #espera receber um pacote UDP de ate 65535 bytes. data contem bytes brutos recebidos
        wrapper = vision_pb.SSL_WrapperPacket() #instancia da classe SSL_WrapperPacket definida no .proto
        wrapper.ParseFromString(data)           #metodo da biblioteca protobuf que decodifica os bytes recebidos em um obj python completo
        return wrapper                          #wrapper tem todos os atributos uteis acessiveis

    #TODO