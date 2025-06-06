from communication.generated import ssl_gc_referee_message_pb2 as referee_pb
from google.protobuf.json_format import MessageToDict

class RefereeParser:
    def __init__(self):
        # Pode ter configurações futuras, se necessário
        pass

    def parse(self, raw_data: bytes) -> referee_pb.Referee: # Converte os dados brutos recebidos (bytes) em um objeto protobuf Referee.

        # Nesse momento, eu optei por usar o objeto protobuf diretamente,
        # mas poderia ser convertido para um dicionário ou outro formato, se necessário.
        # Isso permite acessar os campos do objeto diretamente, como referee_msg.command, referee_msg.stage, etc.
        # Mesmo assim, vou manter o método parse_to_dict para compatibilidade futura.
    
        referee_msg = referee_pb.Referee()
        referee_msg.ParseFromString(raw_data)
        return referee_msg


    def parse_to_dict(self, raw_data: bytes) -> dict:
        referee_msg = referee_pb.Referee()
        referee_msg.ParseFromString(raw_data)

        referee_dict = MessageToDict(
            referee_msg,
            preserving_proto_field_name=True,  # mantém os nomes originais do .proto (snake_case)
            #including_default_value_fields=True,  # inclui campos com valores default
            use_integers_for_enums=True  # enums como inteiros (opcional)
        )

        return referee_dict
