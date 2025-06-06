from communication.vision_receiver import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.parsers.vision_parser import VisionParser
from communication.parsers.referee_parser import RefereeParser

from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb

class WorldState:
    _instance = None

    def __new__(cls, *args, **kwargs):  # Singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, referee_parser: RefereeParser, referee_receiver: RefereeReceiver,
                 vision_parser: VisionParser, vision_receiver: VisionReceiver):
        
        self.referee_receiver = referee_receiver #armazena o objeto q escuta o game controller
        self.referee_parser = referee_parser #armazena o parser do referee. nao é utilizado agora, mas estou deixando disponível aqui pensando em futuras expansões
        self.referee_data: referee_pb.Referee = None #vai armazenar o ultimo pacote decodificado. é um objeto protobuf com campos acessíveis, como referee_data.command, referee_data.stage, etc.

        self.vision_receiver = vision_receiver # armazena o objeto que escuta o SSL-Vision ou o vision do grSim (é a msm coisa)
        self.vision_parser = vision_parser # armazena o parser do vision. nao é utilizado agora, mas estou deixando disponível aqui pensando em futuras expansões
        self.vision_data: dict = None  # dicionário q armazena todos os objetos presentes dentro do pacote vision, como robôs, bolas, etc.


   