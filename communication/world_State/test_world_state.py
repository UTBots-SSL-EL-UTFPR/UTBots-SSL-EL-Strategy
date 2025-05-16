from communication.referee_receiver import RefereeReceiver
from communication.parsers import RefereeParser
from communication.world_State.world_state import world_state
from pprint import pprint
import time

def main():
    # Substitua com o IP da interface de rede usada no Docker, geralmente "172.20.0.1"
    interface_ip="172.17.0.1"

    # Criação dos objetos necessários
    referee_receiver = RefereeReceiver(interface_ip=interface_ip)
    referee_parser = RefereeParser()

    # Instancia o objeto WorldState (singleton)
    ws = world_state(referee_parser, referee_receiver)
    while True:
        ws.update()
        referee_data = ws.get_referee_data()

        print("\n📡 Dados recebidos do GameController:\n")
        pprint(referee_data)

        time.sleep(1)  # Espera 1 segundo antes de tentar receber o próximo pacote

if __name__ == "__main__":
    main()