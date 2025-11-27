import os
from pprint import pprint
from time import sleep

from communication.parsers.referee_parser import RefereeParser
from communication.referee_receiver import RefereeReceiver


def test_referee_receiver():
    receiver = RefereeReceiver(
        interface_ip="172.17.0.1", ip="224.5.23.1", portVision=10003
    )  # IP da interface Docker
    parser = RefereeParser()

    ("Monitorando mensagens do Game Controller...\n")
    try:
        while True:
            message = receiver.get_latest_raw()
            if message:
                parsed = receiver.get_latest_parsed()
                if parsed:
                    parsed_dict = parser.parse_to_dict(
                        message
                    )  # ou diretamente do objeto: parser.protobuf_to_dict(parsed)
                    os.system("clear")  # limpa o terminal para atualizar a visualização
                    ("=== MENSAGEM DO GAME CONTROLLER ===")
                    pprint(parsed_dict)
                else:
                    ("Mensagem recebida, mas não pôde ser parseada.")
            else:
                ("Nenhuma mensagem recebida.")
            sleep(0.1)

    except KeyboardInterrupt:
        ("\nEncerrado pelo usuário.")


if __name__ == "__main__":
    test_referee_receiver()
