from enum import Enum
from time import time
from utils.pose2D import Pose2D
from SSL_configuration.configuration import Configuration

from communication.receiver.vision_receiver import VisionReceiver
from communication.receiver.referee_receiver import RefereeReceiver
from communication.parsers.vision_parser import VisionParser
from communication.parsers.referee_parser import RefereeParser
from Behaviour_tree.core.field_state import FieldState

from communication.generated import ssl_vision_wrapper_pb2 as vision_pb
from communication.generated import ssl_gc_referee_message_pb2 as referee_pb

# =====================================================
# Enum de IDs de robôs
# =====================================================
class RobotID(Enum):
    Kamiji = 0
    Defender = 1 
    Goalkeeper = 2


class World_State:
    _instance = None

    def __init__(self):
        self.configuration = Configuration.getObject()
        try:
            self.vision_receiver = VisionReceiver()
            self.vision_parser = VisionParser()
            self.referee_receiver = RefereeReceiver()
            self.referee_parser = RefereeParser()
            self.field = FieldState()
        except KeyError as e:
            print(e)
            
        self.referee_data: referee_pb.Referee = None # type: ignore
        self.vision_data: dict = {}

        # Dados granulares
        self._robot_positions = {"blue": {}, "yellow": {}}
        self._robot_velocities = {"blue": {}, "yellow": {}}
        self._robot_orientations = {"blue": {}, "yellow": {}}
        self._ball_position: tuple['float','float'] = (0,0)
        self.last_camera_frames = {}

        self._initialized = True

    @staticmethod
    def get_object():
        if not World_State._instance:
            World_State._instance = World_State()
        return World_State._instance

    def update(self, timeout=0.01):
        """Atualiza árbitro e visão considerando múltiplas câmeras por ciclo."""
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


    def get_ball_position(self):
        position = self._ball_position
        return Pose2D(int(position[0]), int(position[1]))
    
    #team
    def get_team_robot_pose(self, robot_id: int) -> Pose2D | None:
        team_color = self.configuration.team_collor
        if not team_color:
            return None
        if robot_id not in self._robot_positions.get(team_color, {}):
            return None
        x, y = self._robot_positions[team_color][robot_id]
        theta = self._robot_orientations[team_color][robot_id]
        return Pose2D(int(x), int(y), theta)

    def get_team_robot_velocity(self, robot_id: int) -> Pose2D | None:
        team_color = self.configuration.team_collor
        if not team_color:
            return None
        if robot_id not in self._robot_velocities.get(team_color, {}):
            return None
        vx, vy = self._robot_velocities[team_color][robot_id]
        theta = self._robot_orientations[team_color][robot_id]
        return Pose2D(int(vx), int(vy), theta)
    
    #foes
    def get_foe_robot_pose(self, robot_id: int) -> Pose2D | None:
        foes_collor = self.configuration.foes_collor
        if not foes_collor:
            return None
        if robot_id not in self._robot_positions.get(foes_collor, {}):
            return None
        x, y = self._robot_positions[foes_collor][robot_id]
        theta = self._robot_orientations[foes_collor][robot_id]
        pos = Pose2D(int(x), int(y), theta)
        pos.get_quadrant()
        return pos

    def get_foe_robot_velocity(self, robot_id: int) -> Pose2D | None:
        foes_collor = self.configuration.foes_collor
        if not foes_collor:
            return None
        if robot_id not in self._robot_velocities.get(foes_collor, {}):
            return None
        vx, vy = self._robot_velocities[foes_collor][robot_id]
        theta = self._robot_orientations[foes_collor][robot_id]
        return Pose2D(int(vx), int(vy), theta)
