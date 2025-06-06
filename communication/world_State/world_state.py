from communication.vision_receiver import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.referee_receiver import RefereeParser
from communication.vision_receiver import VisionParser
from communication.field_state import FieldState

from time import time

class world_state:
    _instance = None

    def __new__(cls, *args, **kwargs):  # Singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, refereeP: RefereeParser, refereeR: RefereeReceiver,
                 visionP: VisionParser, visionR: VisionReceiver, fs: FieldState):
        self.referee_receiver = refereeR
        self.referee_parser = refereeP
        self.referee_data = None

        self.vision_receiver = visionR
        self.vision_parser = visionP
        self.vision_data = None

        self.field_state = fs

    def update(self, timeout=0.3):
        start_time = time()
        received_cameras = set()

        while time() - start_time < timeout:
            # Atualiza visão (multi-câmera)
            raw_vision_data = self.vision_receiver.receive_raw()
            if raw_vision_data:
                parsed = self.vision_parser.parse_to_dict(raw_vision_data)
                cam_id = parsed.get("detection", {}).get("camera_id")
                if cam_id is not None and cam_id not in received_cameras:
                    self.vision_data = parsed
                    self.field_state.update_from_packet(parsed)
                    received_cameras.add(cam_id)

            # Atualiza referee independentemente
            raw_ref_data = self.referee_receiver.receive_raw()
            if raw_ref_data:
                self.referee_data = self.referee_parser.parse_to_dict(raw_ref_data)

    def get_field_state(self):
        return self.field_state.get_state()

    def get_vision_data(self):
        return self.vision_data

    def get_referee_data(self):
        return self.referee_data
