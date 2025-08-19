from communication.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from Behaviour_tree.core.field_state import FieldState
from time import time, sleep
from pprint import pprint
import os

def test_vision_receiver(interface_ip="0.0.0.0", timeout=0.3):
    # Inicializa o receiver para receber pacotes UDP do SSL-Vision
    receiver = VisionReceiver(interface_ip=interface_ip,ip="224.5.23.2",portVision=10020)

    # Inicializa o parser que traduz os pacotes brutos em dicionários Python
    parser = VisionParser()

    # Inicializa o objeto que manterá o estado consolidado do campo
    field = FieldState()

    print(f"Iniciando monitoramento completo com timeout de {timeout:.1f}s por ciclo...\n")

    last_processed_raw = None
    
    try:
        while True:
            # Conjunto para rastrear quais câmeras já foram recebidas neste ciclo
            received_cameras = set()
            start_time = time()

            # Laço interno que coleta pacotes até o timeout definido por ciclo
            while time() - start_time < timeout:
                raw = receiver.get_latest_raw()
                if raw is not None and raw != last_processed_raw:
                    last_processed_raw = raw  # marca como já processado
                    parsed = parser.parse_to_dict(raw)
                    cam_id = parsed.get("detection", {}).get("camera_id")
                    if cam_id is not None and cam_id not in received_cameras:
                        field.update_from_packet(parsed)
                        received_cameras.add(cam_id)

            # Limpa o terminal antes de mostrar o estado atualizado
            os.system("clear")  # Em Windows, use "cls"

            # Mostra o estado consolidado com número de câmeras recebidas
            print(f"=== ESTADO COMPLETO DO CAMPO — câmeras recebidas: {len(received_cameras)} ===\n")
            pprint(field.get_state())  # Exibe todos os dados atuais do campo (robôs, bola, etc.)

            # Aguarda brevemente antes de começar o próximo ciclo
            sleep(0.1)

    except KeyboardInterrupt:
        # Permite encerrar o monitoramento com Ctrl+C
        print("\n Monitoramento encerrado pelo usuário.")

# Quando o script é executado diretamente, inicia o monitoramento
if __name__ == "__main__":
    test_vision_receiver()
