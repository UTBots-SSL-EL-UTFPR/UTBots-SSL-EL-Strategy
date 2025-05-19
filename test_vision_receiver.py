from communication.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from pprint import pprint

def test_vision_receiver():
    receiver = VisionReceiver(interface_ip="0.0.0.0")  # IP da interface Docker
    message = receiver.receive_raw()  # Recebe pacote bruto do SSL-Vision

    if message:
        parser = VisionParser()
        parsed = parser.parse_to_dict(message)

        print("=== Dados do SSL-Vision ===")
        pprint(parsed)
    else:
        print("Nenhum dado recebido do SSL-Vision.")

if __name__ == "__main__":
    test_vision_receiver()
