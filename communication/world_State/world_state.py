#from communication.vision_receiver  import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.referee_receiver import RefereeParser
#from communication.vision_receiver import VisionParser

#implementaçao apenas do prototipo da classe world_state que tera os objetos do tipo referee e vision
#visando um maior desacoplamento do codigo

class world_state:
    _instance=None
    
    def __new__(cls, *args , **kwargs):  #singlenton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self,refereeP:RefereeParser,refereeR:RefereeReceiver):
        self.referee_receiver = refereeR #cria o Objeto da classe referee_receiver
        self.referee_parser = refereeP #cria o objeto da classe referee_parser
        self.referee_data = None

    def update(self):
        raw_data = self.referee_receiver.receive_raw()#pego os dados brutos do refeere receiver
        if raw_data:
            self.referee_data = self.referee_parser.parse_to_dict(raw_data)#interpretaçao dos dados brutos atraves do refereee parser e atualizacao do estado interno referee data 
        

    def get_vision_data(self):
        pass
    #TODO

    def get_referee_data(self):
        return self.referee_data
    