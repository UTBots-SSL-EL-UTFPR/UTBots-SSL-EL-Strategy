from communication.vision_receiver import VisionReceiver
from communication.referee_receiver import RefereeReceiver
from communication.parsers.vision_parser import VisionParser
from communication.parsers.referee_parser import RefereeParser
from communication.field_state import FieldState

from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb

from time import time

class WorldState:
    _instance = None

    def __new__(cls, *args, **kwargs):  # Singleton
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, referee_parser: RefereeParser, referee_receiver: RefereeReceiver,
                 vision_parser: VisionParser, vision_receiver: VisionReceiver,
                 field: FieldState):

        if hasattr(self, "_initialized") and self._initialized:
            return  # Já inicializado

        self.referee_receiver = referee_receiver
        self.referee_parser = referee_parser
        self.referee_data: referee_pb.Referee = None

        self.vision_receiver = vision_receiver
        self.vision_parser = vision_parser
        self.vision_data: dict = None

        self.field = field

        self._initialized = True

    def update(self, timeout=0.3):
        """Atualiza estado de árbitro e visão considerando múltiplas câmeras por ciclo."""

        # Atualiza árbitro (1 pacote por ciclo)
        self.referee_data = self.referee_receiver.get_latest_parsed()

        # Atualiza visão com múltiplas câmeras
        last_processed_raw = None
        received_cameras = set()
        start_time = time()

        while time() - start_time < timeout:
            raw = self.vision_receiver.get_latest_raw()
            if raw and raw != last_processed_raw:
                last_processed_raw = raw
                parsed = self.vision_parser.parse_to_dict(raw)
                cam_id = parsed.get("detection", {}).get("camera_id")

                if cam_id is not None and cam_id not in received_cameras:
                    self.vision_data = parsed
                    self.field.update_from_packet(parsed)
                    received_cameras.add(cam_id)

    def get_referee_data(self):
        return self.referee_data

    def get_vision_data(self):
        return self.vision_data

    def get_field_state(self):
        return self.field.get_state()
