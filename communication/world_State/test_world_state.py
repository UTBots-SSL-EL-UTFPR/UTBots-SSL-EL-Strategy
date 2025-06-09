from communication.vision_receiver import VisionReceiver
from communication.vision_receiver import VisionParser
from communication.referee_receiver import RefereeReceiver, RefereeParser
from communication.field_state import FieldState
from communication.world_State.world_state import WorldState

import time
import os
from pprint import pprint

def test_world_state(interface_ip_referee="172.17.0.1", interface_ip_vision="0.0.0.0", timeout=0.3):
    print("Iniciando teste do world_state...")

    vision_receiver = VisionReceiver(interface_ip=interface_ip_vision, ip="224.5.23.2",portVision=10020)
    vision_parser = VisionParser()
    referee_receiver = RefereeReceiver(interface_ip=interface_ip_referee,ip="224.5.23.1",portVision=10003)
    referee_parser = RefereeParser()
    field_state = FieldState()

    ws = WorldState(referee_parser, referee_receiver, vision_parser, vision_receiver, field_state)

    try:
        while True:
            ws.update(timeout=timeout)

            vision = ws.get_vision_data()
            referee = ws.get_referee_data()
            field = ws.get_field_state()

            os.system("clear")  # "cls" no Windows

            print("=== WORLD STATE ===\n")

            if vision:
                print("[VISION] Bola:")
                pprint(vision.get('ball'))
            else:
                print("[VISION] Nenhum dado recebido.")

            if referee:
                print("\n[REFEREE] Estado do jogo:")
                pprint(referee)
            else:
                print("\n[REFEREE] Nenhum dado recebido.")

            print("\n[FIELD_STATE] Times e robôs:")
            pprint(field)

            print("\n" + "="*50)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nTeste encerrado pelo usuário.")

if __name__ == "__main__":
    test_world_state()
