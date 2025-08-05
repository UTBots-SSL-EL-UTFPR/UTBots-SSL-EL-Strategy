from communication.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from communication.referee_receiver import RefereeReceiver
from communication.parsers.referee_parser import RefereeParser
from communication.field_state import FieldState
from communication.world_State.world_state import WorldState

from time import time, sleep
from pprint import pprint
import os

def test_world_state(interface_ip_referee="172.17.0.1", interface_ip_vision="0.0.0.0", timeout=0.3):
    print(f"Iniciando teste do WorldState com timeout de {timeout:.1f}s por ciclo...")

    # Inicializa os componentes
    vision_receiver = VisionReceiver(interface_ip=interface_ip_vision, ip="224.5.23.2", portVision=10020)
    vision_parser = VisionParser()
    referee_receiver = RefereeReceiver(interface_ip=interface_ip_referee, ip="224.5.23.1", portVision=10003)
    referee_parser = RefereeParser()
    field_state = FieldState()

    # Inicializa estado global (singleton)
    ws = WorldState(referee_parser, referee_receiver, vision_parser, vision_receiver, field_state)

    last_processed_raw = None

    try:
        while True:
            received_cameras = set()
            start_time = time()

            # Coleta pacotes de múltiplas câmeras dentro do timeout
            while time() - start_time < timeout:
                raw = vision_receiver.get_latest_raw()
                if raw and raw != last_processed_raw:
                    last_processed_raw = raw
                    parsed = vision_parser.parse_to_dict(raw)
                    cam_id = parsed.get("detection", {}).get("camera_id")
                    if cam_id is not None and cam_id not in received_cameras:
                        ws.vision_data = parsed
                        ws.field.update_from_packet(parsed)
                        received_cameras.add(cam_id)

            # Atualiza árbitro
            ws.referee_data = referee_receiver.get_latest_parsed()

            # Limpa terminal
            os.system("clear")

            # Exibe estado do mundo
            print(f"=== ESTADO GLOBAL DO CAMPO — câmeras recebidas: {len(received_cameras)} ===\n")

            print("[FIELD STATE]")
            pprint(ws.get_field_state())


            print("\n[REFEREE]")
            referee_data = ws.get_referee_data()
            if referee_data:
                print(f"Stage: {referee_data.stage}, Command: {referee_data.command}")
            else:
                print("Nenhum dado recebido do árbitro.")

            print("\n[ULTIMA CÂMERA VISÃO]")
            vision_data = ws.get_vision_data()
            if vision_data:
                print(f"Camera ID: {vision_data.get('detection', {}).get('camera_id')}")
            else:
                print("Nenhum dado de visão disponível.")

            print("\n" + "="*50)
            sleep(0.1)

    except KeyboardInterrupt:
        print("\nTeste encerrado pelo usuário.")

if __name__ == "__main__":
    test_world_state()
