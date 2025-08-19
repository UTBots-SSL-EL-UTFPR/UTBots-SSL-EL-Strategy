from communication.receiver.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from communication.receiver.referee_receiver import RefereeReceiver
from communication.parsers.referee_parser import RefereeParser
from Behaviour_tree.core.field_state import FieldState
from Behaviour_tree.core.World_State import World_State, RobotID

from time import time, sleep
from pprint import pprint
import os

# Comando pra rodar python3 -m Behaviour_tree.core.test_World_State

def test_World_State(timeout=0.3):
    print(f"Iniciando teste do WorldState com timeout de {timeout:.1f}s por ciclo...")
    sleep(1)
    ws = World_State()

    try:
        while True:
            # Atualiza estado completo do mundo (árbitro + visão múltiplas câmeras)
            ws.update(timeout=timeout)

            # Limpa terminal
            os.system("clear")

            # Exibe estado do mundo
            print("=== ESTADO GLOBAL DO CAMPO ===\n")

            # Snapshot do FieldState
            # print("[FIELD SNAPSHOT]")
            # pprint(ws.get_field_snapshot())

            # Detalhes granulares de robôs
            print("\n[ROBÔS - POSIÇÕES, VELOCIDADES E ORIENTAÇÕES]")
        
            for rid in [1,2,3]:
                pos = ws.get_team_robot_pose(rid)
                vel = ws.get_team_robot_velocity(rid)
                print(f"{rid}: Pos={pos}, Vel={vel}")

            print("\n[REFEREE]")
            referee_data = ws.get_referee_data()
            if referee_data:
                print(f"Stage: {referee_data.stage}, Command: {referee_data.command}")
            else:
                print("Nenhum dado recebido do árbitro.")

            print("\n[ÚLTIMA CÂMERA VISÃO]")
            vision_data = ws.get_vision_data()
            if vision_data:
                print(f"Camera ID: {vision_data.get('detection', {}).get('camera_id')}")
            else:
                print("Nenhum dado de visão disponível.")

            print("\n" + "="*50)
            sleep(0.5)

    except KeyboardInterrupt:
        print("\nTeste encerrado pelo usuário.")

if __name__ == "__main__":
    test_World_State()

