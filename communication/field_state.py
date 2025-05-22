from collections import defaultdict

class FieldState:
    def __init__(self):
        self.robots_blue = defaultdict(dict)
        self.robots_yellow = defaultdict(dict)
        self.balls = []
        self.geometry = None
        self.last_camera_frames = {}  # camera_id -> metadata por câmera

    def update_from_packet(self, packet: dict):
        # Atualiza geometria (vem apenas de tempos em tempos)
        if "geometry" in packet:
            self.geometry = packet["geometry"]

        # Atualiza estado a partir de dados de detecção (frame por câmera)
        detection = packet.get("detection")
        if detection:
            camera_id = detection.get("camera_id")
            frame_number = detection.get("frame_number")
            t_capture = detection.get("t_capture")
            t_sent = detection.get("t_sent")

            # Armazena metadata do frame mais recente dessa câmera
            self.last_camera_frames[camera_id] = {
                "frame_number": frame_number,
                "t_capture": t_capture,
                "t_sent": t_sent
            }

            # Robôs azuis
            for bot in detection.get("robots_blue", []):
                robot_id = bot["robot_id"]
                self.robots_blue[robot_id] = bot

            # Robôs amarelos
            for bot in detection.get("robots_yellow", []):
                robot_id = bot["robot_id"]
                self.robots_yellow[robot_id] = bot

            # Bolas (aqui você pode aplicar filtros se quiser evitar duplicação)
            for ball in detection.get("balls", []):
                self.balls.append(ball)

    def get_state(self):
        """Retorna o estado atual consolidado do campo."""
        return {
            "robots_blue": dict(self.robots_blue),
            "robots_yellow": dict(self.robots_yellow),
            "balls": self.balls,
            "geometry": self.geometry,
            "frames_metadata": self.last_camera_frames
        }
