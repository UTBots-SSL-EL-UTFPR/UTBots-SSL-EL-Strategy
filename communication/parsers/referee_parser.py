from communication.generated import ssl_gc_referee_message_pb2 as referee_pb

class RefereeParser:
    def __init__(self):
        # Pode ter configurações futuras, se necessário
        pass

    def parse(self, raw_data: bytes) -> referee_pb.Referee:
        """Decodifica os dados brutos em um objeto Referee."""
        referee_msg = referee_pb.Referee()
        referee_msg.ParseFromString(raw_data)
        return referee_msg
