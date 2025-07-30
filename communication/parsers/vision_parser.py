from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from google.protobuf.json_format import MessageToDict

class VisionParser:
    def __init__(self):
        # Pode conter configurações futuras
        pass

    def parse(self, raw_data: bytes) -> vision_pb.SSL_WrapperPacket: # Converte os dados brutos recebidos (bytes) em um objeto protobuf SSL_WrapperPacket.

        # Nesse momento, eu optei por usar o objeto protobuf diretamente,
        # mas poderia ser convertido para um dicionário ou outro formato, se necessário.
        # Isso permite acessar os campos do objeto diretamente, como vision_msg.detection, vision_msg.robots_blue, etc.
        # Mesmo assim, vou manter o método parse_to_dict para compatibilidade futura.
    
        vision_msg = vision_pb.SSL_WrapperPacket()
        vision_msg.ParseFromString(raw_data)
        return vision_msg


    def parse_to_dict(self, raw_data: bytes) -> dict:
        """Converte os dados brutos do SSL-Vision em um dicionário estruturado."""
        vision_msg = vision_pb.SSL_WrapperPacket()
        vision_msg.ParseFromString(raw_data)

        vision_dict = MessageToDict(
            vision_msg,
            preserving_proto_field_name=True,        # mantém nomes do .proto
            #including_default_value_fields=True,     # inclui campos default
            use_integers_for_enums=True              # enums como inteiros
        )

        return vision_dict
