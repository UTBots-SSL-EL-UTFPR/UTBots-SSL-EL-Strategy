from communication.vision_receiver import VisionReceiver
from communication.vision_receiver import VisionParser
from communication.referee_receiver import RefereeReceiver, RefereeParser
from communication.field_state import FieldState

from communication.world_State.world_state import world_state

import time

def main():
    interface_ip = "10.23.0.57" # Substitua pelo IP correto da sua rede
    print("Iniciando teste do world_state...")
    vision_receiver = VisionReceiver(interface_ip=interface_ip)
    vision_parser = VisionParser()
    referee_receiver = RefereeReceiver(interface_ip=interface_ip)
    referee_parser = RefereeParser()
    field_state = FieldState()

    ws = world_state(referee_parser, referee_receiver, vision_parser, vision_receiver, field_state)

    # Loop principal
    while True:
        ws.update()

        vision = ws.get_vision_data()
        referee = ws.get_referee_data()
        field = ws.get_field_state()

        if vision:
            print("[VISION] Bola:", vision.get('ball'))
        else:
            print("[VISION] Nenhum dado recebido.")

        if referee:
            print("[REFEREE] Fase:", referee.get('stage'))
        else:
            print("[REFEREE] Nenhum dado recebido.")

        if field:
            print("[FIELD_STATE] Times:")
            for team, data in field.items():
                print(f" - {team}: {data}")
        else:
            print("[FIELD_STATE] Ainda não atualizado.")

        print("="*40)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
