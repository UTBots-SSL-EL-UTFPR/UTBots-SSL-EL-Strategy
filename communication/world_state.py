from communication.vision_receiver  import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.referee_receiver import RefereeParser
#from communication.vision_receiver import VisionParser

#implementaçao apenas do prototipo da classe world_state que tera os objetos do tipo referee e vision
#visando um maior desacoplamento do codigo

class world_state:
    def __init__(self,visionR:VisionReceiver,refereeR:RefereeReceiver,refereeP:RefereeParser):
        pass
    #TODO

    def update(self):
        pass
    #TODO

    def get_vision_data(self):
        pass
    #TODO

    def get_referee_data(self):
        pass
    #TODO