from communication.referee_receiver import RefereeReceiver
from communication.parsers.referee_parser import RefereeParser
from pprint import pprint
from time import sleep
import os

def test_referee_receiver():
    receiver = RefereeReceiver(interface_ip="172.17.0.1",ip="224.5.23.1",portVision=10003)  # IP da interface Docker
    parser = RefereeParser()

    print("Monitorando mensagens do Game Controller...\n")
    try:
        while True:
            message = receiver.receive_raw()
            if message:
                parsed = parser.parse_to_dict(message)
                os.system("clear")  # limpa o terminal para atualizar a visualização
                print("=== MENSAGEM DO GAME CONTROLLER ===")
                pprint(parsed)
            else:
                print("Nenhuma mensagem recebida.")
            sleep(0.1)  # pequeno atraso para evitar spam do terminal

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

if __name__ == "__main__":
    test_referee_receiver()
