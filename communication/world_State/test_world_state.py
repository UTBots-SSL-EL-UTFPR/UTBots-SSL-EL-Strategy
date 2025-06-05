from communication.vision_receiver import VisionReceiver
from communication.vision_receiver import VisionParser
from communication.referee_receiver import RefereeReceiver, RefereeParser
from communication.field_state import FieldState
from communication.world_State.world_state import world_state

import time
import os
from pprint import pprint

def test_world_state(interface_ip_referee="0.0.0.0", interface_ip_vision="0.0.0.0", timeout=0.5):
    print("Iniciando teste do world_state...")

    vision_receiver = VisionReceiver(interface_ip=interface_ip_vision)
    vision_parser = VisionParser()
    referee_receiver = RefereeReceiver(interface_ip=interface_ip_referee)
    referee_parser = RefereeParser()
    field_state = FieldState()

    ws = world_state(referee_parser, referee_receiver, vision_parser, vision_receiver, field_state)

    try:
        while True:
            start_time = time.time()
            ws.update()

            vision = ws.get_vision_data()
            referee = ws.get_referee_data()
            field = ws.get_field_state()

            os.system("clear")  # limpa tela, use "cls" no Windows

            print("=== World State Atualizado ===\n")

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

            if field:
                print("\n[FIELD_STATE] Times e robôs:")
                pprint(field)
            else:
                print("\n[FIELD_STATE] Ainda não atualizado.")

            print("\n" + "="*50)

            elapsed = time.time() - start_time
            sleep_time = max(0, timeout - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nTeste encerrado pelo usuário.")

if __name__ == "__main__":
    test_world_state()
