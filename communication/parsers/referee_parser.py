from communication.generated import ssl_gc_referee_message_pb2 as referee_pb
from google.protobuf.json_format import MessageToDict

class RefereeParser:
    def __init__(self):
        # Pode ter configurações futuras, se necessário
        pass

    def parse_to_dict(self, raw_data: bytes) -> dict:
        referee_msg = referee_pb.Referee()
        referee_msg.ParseFromString(raw_data)

        referee_dict = MessageToDict(
            referee_msg,
            preserving_proto_field_name=True,  # mantém os nomes originais do .proto (snake_case)
            including_default_value_fields=True,  # inclui campos com valores default
            use_integers_for_enums=True  # enums como inteiros (opcional)
        )

        return referee_dict
