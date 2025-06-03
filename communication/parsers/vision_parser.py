from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from google.protobuf.json_format import MessageToDict

class VisionParser:
    def __init__(self):
        # Pode conter configurações futuras
        pass

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
