from communication.vision_receiver  import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.referee_receiver import RefereeParser
from communication.vision_receiver import VisionParser
from communication.field_state import FieldState

#implementaçao apenas do prototipo da classe world_state que tera os objetos do tipo referee e vision
#visando um maior desacoplamento do codigo

class world_state:
    _instance=None
    
    def __new__(cls, *args , **kwargs):  #singlenton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self,refereeP:RefereeParser,refereeR:RefereeReceiver,visionP:VisionParser,visionR:VisionReceiver,fs:FieldState):
        #Referee
        self.referee_receiver = refereeR #cria o Objeto da classe referee_receiver
        self.referee_parser = refereeP #cria o objeto da classe referee_parser
        self.referee_data = None
        
        #Vision/Field_state
        #cria os objetos das classes vision Receiver/parser e field state
        self.vision_receiver = visionR
        self.vison_parser = visionP
        self.vision_data=None
        self.field_state = fs
        

    def update(self):
        #Atualiza os dados do referee 
        raw_ref_data = self.referee_receiver.receive_raw()#pego os dados brutos do refeere receiver
        if raw_ref_data:
            self.referee_data = self.referee_parser.parse_to_dict(raw_ref_data)#interpretaçao dos dados brutos atraves do refereee parser e atualizacao do estado interno referee data 

        raw_vision_data = self.vision_receiver.receive_raw()#pego os dados brutos do vision receiver
        if raw_vision_data:
            self.vision_data = self.vison_parser.parse_to_dict(raw_vision_data)
            self.field_state.update_from_packet(self.vision_data)
    
    def get_field_state(self):
        return self.field_state.get_state()

    def get_vision_data(self):
        return self.vision_data

    def get_referee_data(self):
        return self.referee_data
    