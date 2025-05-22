from communication.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser
from pprint import pprint
from time import time

from communication.field_state import FieldState

def test_vision_receiver():
    receiver = VisionReceiver(interface_ip="0.0.0.0")
    parser = VisionParser()
    field = FieldState()

    print("Recebendo pacotes de múltiplas câmeras...")

    received_cameras = set()
    max_cameras = 4
    timeout = 5
    start_time = time()

    while len(received_cameras) < max_cameras and time() - start_time < timeout:
        raw = receiver.receive_raw()
        if raw:
            parsed = parser.parse_to_dict(raw)
            cam_id = parsed.get("detection", {}).get("camera_id")
            if cam_id not in received_cameras:
                field.update_from_packet(parsed)
                received_cameras.add(cam_id)

    print("\n=== Estado Consolidado do Campo ===")
    pprint(field.get_state())

if __name__ == "__main__":
    test_vision_receiver()
