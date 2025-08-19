from dataclasses import dataclass, field
@dataclass


class FieldState:
    def __init__(self):
        # Dicionários para armazenar dados dos robôs azuis e amarelos.
        self.robots_blue = {}
        self.robots_yellow = {}
        self.ball = None
        self.ball_t_capture = -1
        self.geometry = None
        self.last_camera_frames = {}  # chave: camera_id

    def update_from_packet(self, packet: dict):
        """
        Atualiza a geometria do campo, se estiver presente no pacote
        """
        if "geometry" in packet:
            self.geometry = packet["geometry"]

        detection = packet.get("detection")
        if detection:
            camera_id = detection.get("camera_id")
            frame_number = detection.get("frame_number")
            t_capture = detection.get("t_capture")  
            t_sent = detection.get("t_sent")        

            self.last_camera_frames[camera_id] = {
                "frame_number": frame_number,
                "t_capture": t_capture,
                "t_sent": t_sent
            }

            for bot in detection.get("robots_blue", []):
                robot_id = bot["robot_id"]
                self.robots_blue[robot_id] = bot

            for bot in detection.get("robots_yellow", []):
                robot_id = bot["robot_id"]
                self.robots_yellow[robot_id] = bot

            for ball in detection.get("balls", []):
                if t_capture > self.ball_t_capture:
                    self.ball = ball
                    self.ball_t_capture = t_capture

    def get_state(self):
        """Retorna o estado atual consolidado do campo."""
        return {
            "robots_blue": dict(self.robots_blue),          # Converte defaultdict para dict comum
            "robots_yellow": dict(self.robots_yellow),
            "ball": self.ball,                              # Verifica a bola mais recente
            "geometry": self.geometry,                      # Informações sobre o campo
            "frames_metadata": self.last_camera_frames      # Informações por câmera
        }
