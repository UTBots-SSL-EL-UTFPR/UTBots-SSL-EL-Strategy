from communication.receiver.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from communication.receiver.referee_receiver import RefereeReceiver
from communication.parsers.referee_parser import RefereeParser
from communication.field_state import FieldState
from Behaviour_tree.core.World_State import World_State, RobotID

from time import time, sleep
from pprint import pprint
import os

# Comando pra rodar python3 -m Behaviour_tree.core.test_World_State

def test_World_State(interface_ip_referee="172.17.0.1", interface_ip_vision="0.0.0.0", timeout=0.3):
    print(f"Iniciando teste do WorldState com timeout de {timeout:.1f}s por ciclo...")

    # Inicializa os componentes
    vision_receiver = VisionReceiver(interface_ip=interface_ip_vision, ip="224.5.23.2", portVision=10020)
    vision_parser = VisionParser()
    referee_receiver = RefereeReceiver(interface_ip=interface_ip_referee, ip="224.5.23.1", portVision=10003)
    referee_parser = RefereeParser()
    field_state = FieldState()

    # Inicializa estado global (singleton)
    ws = World_State(referee_receiver, referee_parser, vision_receiver, vision_parser, field_state)

    try:
        while True:
            # Atualiza estado completo do mundo (árbitro + visão múltiplas câmeras)
            ws.update(timeout=timeout)

            # Limpa terminal
            os.system("clear")

            # Exibe estado do mundo
            print("=== ESTADO GLOBAL DO CAMPO ===\n")

            # Snapshot do FieldState
            print("[FIELD SNAPSHOT]")
            pprint(ws.get_field_snapshot())

            # Detalhes granulares de robôs
            print("\n[ROBÔS - POSIÇÕES, VELOCIDADES E ORIENTAÇÕES]")
            for team in ["blue", "yellow"]:
                for rid in ws._robot_positions[team].keys():
                    pos = ws.get_robot_position(team, rid)
                    vel = ws.get_robot_velocity(team, rid)
                    ori = ws.get_robot_orientation(team, rid)
                    print(f"{team.upper()} {rid}: Pos={pos}, Vel={vel}, Ori={ori:.2f}")

            # Dados do árbitro
            print("\n[REFEREE]")
            referee_data = ws.get_referee_data()
            if referee_data:
                print(f"Stage: {referee_data.stage}, Command: {referee_data.command}")
            else:
                print("Nenhum dado recebido do árbitro.")

            # Última câmera de visão
            print("\n[ÚLTIMA CÂMERA VISÃO]")
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
    test_World_State()
