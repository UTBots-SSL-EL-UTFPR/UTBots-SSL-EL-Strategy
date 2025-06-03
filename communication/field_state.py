from collections import defaultdict

class FieldState:
    def __init__(self):
        # Dicionários para armazenar dados dos robôs azuis e amarelos.
        # defaultdict com dict permite acessar chaves inexistentes sem erro.
        self.robots_blue = defaultdict(dict)
        self.robots_yellow = defaultdict(dict)

        # Variável para armazenar a bola mais recente detectada no campo
        self.ball = None

        # Timestamp da captura mais recente da bola, usado para garantir que apenas a bola maovais n seja mantida
        self.ball_t_capture = -1

        # Geometria do campo (informações sobre as dimensões, áreas, etc.)
        self.geometry = None

        # Metadados do último frame recebido por câmera: frame_number, t_capture, t_sent
        self.last_camera_frames = {}  # chave: camera_id

    def update_from_packet(self, packet: dict):
        # Atualiza a geometria do campo, se estiver presente no pacote
        if "geometry" in packet:
            self.geometry = packet["geometry"]

        # Extrai e processa dados de detecção (normalmente fornecidos por câmera)
        detection = packet.get("detection")
        if detection:
            # Identificadores e timestamps do frame atual
            camera_id = detection.get("camera_id")
            frame_number = detection.get("frame_number")
            t_capture = detection.get("t_capture")  # timestamp da captura pela câmera
            t_sent = detection.get("t_sent")        # timestamp de envio da câmera

            # Armazena os metadados do último frame recebido dessa câmera
            self.last_camera_frames[camera_id] = {
                "frame_number": frame_number,
                "t_capture": t_capture,
                "t_sent": t_sent
            }

            # Atualiza dados dos robôs azuis
            for bot in detection.get("robots_blue", []):
                robot_id = bot["robot_id"]
                self.robots_blue[robot_id] = bot  # Substitui ou insere os dados do robô

            # Atualiza dados dos robôs amarelos
            for bot in detection.get("robots_yellow", []):
                robot_id = bot["robot_id"]
                self.robots_yellow[robot_id] = bot

            # Atualiza a bola apenas se for mais recente que a anterior registrada
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
