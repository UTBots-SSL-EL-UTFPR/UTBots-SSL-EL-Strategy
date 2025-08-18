from enum import Enum
from time import time

from ...communication.receiver.vision_receiver import VisionReceiver
from ...communication.receiver.referee_receiver import RefereeReceiver
from ...communication.parsers.vision_parser import VisionParser
from ...communication.parsers.referee_parser import RefereeParser
from ...communication.field_state import FieldState

from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb

# =====================================================
# Enum de IDs de robôs
# =====================================================
class RobotID(Enum):
    Kamiji = "Kamiji"
    Defender = "Defender"
    Goalkeeper = "GOALKEEPER"


class World_State:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, referee_receiver: RefereeReceiver, referee_parser: RefereeParser,
                 vision_receiver: VisionReceiver, vision_parser: VisionParser,
                 field: FieldState):

        if hasattr(self, "_initialized") and self._initialized:
            return

        # Receivers e parsers
        self.referee_receiver = referee_receiver
        self.referee_parser = referee_parser
        self.referee_data: referee_pb.Referee = None #????

        self.vision_receiver = vision_receiver
        self.vision_parser = vision_parser
        self.vision_data: dict = {}

        # FieldState
        self.field = field

        # Dados granulares
        self._robot_positions = {"blue": {}, "yellow": {}}
        self._robot_velocities = {"blue": {}, "yellow": {}}
        self._robot_orientations = {"blue": {}, "yellow": {}}
        self._ball_position = (0.0, 0.0)
        self.last_camera_frames = {}

        self._initialized = True

    def update(self, timeout=0.3):
        """Atualiza árbitro e visão considerando múltiplas câmeras por ciclo."""
        # Árbitro
        self.referee_data = self.referee_receiver.get_latest_parsed()

        # Visão
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
                    self._update_granular(parsed)
                    received_cameras.add(cam_id)

    def _update_granular(self, packet: dict):
        detection = packet.get("detection")
        if not detection:
            return

        camera_id = detection.get("camera_id")
        frame_number = detection.get("frame_number")
        t_capture = detection.get("t_capture")
        t_sent = detection.get("t_sent")

        self.last_camera_frames[camera_id] = {
            "frame_number": frame_number,
            "t_capture": t_capture,
            "t_sent": t_sent
        }

        # Robôs
        robots_blue = {r["robot_id"]: r for r in detection.get("robots_blue", [])}
        robots_yellow = {r["robot_id"]: r for r in detection.get("robots_yellow", [])}

        # Bola
        balls = detection.get("balls", [])
        if balls:
            self._ball_position = (balls[0]["x"], balls[0]["y"])

        # Atualiza posições, velocidades e orientações
        for bot in detection.get("robots_blue", []):
            rid = bot["robot_id"]
            self._robot_positions["blue"][rid] = (bot.get("x", 0.0), bot.get("y", 0.0))
            self._robot_velocities["blue"][rid] = (bot.get("vx", 0.0), bot.get("vy", 0.0))
            self._robot_orientations["blue"][rid] = bot.get("orientation", 0.0)

        for bot in detection.get("robots_yellow", []):
            rid = bot["robot_id"]
            self._robot_positions["yellow"][rid] = (bot.get("x", 0.0), bot.get("y", 0.0))
            self._robot_velocities["yellow"][rid] = (bot.get("vx", 0.0), bot.get("vy", 0.0))
            self._robot_orientations["yellow"][rid] = bot.get("orientation", 0.0)


    def get_referee_data(self):
        return self.referee_data

    def get_vision_data(self):
        return self.vision_data

    def get_field_snapshot(self):
        """Retorna estado completo do campo, incluindo robôs, bola e frames."""
        return {
            "robots_blue": self.field.robots_blue,
            "robots_yellow": self.field.robots_yellow,
            "ball_position": self._ball_position,
            "frames_metadata": self.last_camera_frames,
            "granular": {
                "positions": self._robot_positions,
                "velocities": self._robot_velocities,
                "orientations": self._robot_orientations,
            }
        }

    def get_robot_position(self, team: str, robot_id: int):
        return self._robot_positions.get(team, {}).get(robot_id, (0.0, 0.0))

    def get_robot_velocity(self, team: str, robot_id: int):
        return self._robot_velocities.get(team, {}).get(robot_id, (0.0, 0.0))

    def get_robot_orientation(self, team: str, robot_id: int):
        return self._robot_orientations.get(team, {}).get(robot_id, 0.0)


