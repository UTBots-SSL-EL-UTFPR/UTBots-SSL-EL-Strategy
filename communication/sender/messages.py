import struct
from dataclasses import dataclass

# IDs (ajuste se o firmware usar outros)
MSG_ID_CMD  = 100
MSG_ID_PING = 101

# Protocolo binário (11 bytes, little-endian), compatível com o firmware
PACK_FMT = '<BBhhhh?'
PACK_SIZE = struct.calcsize(PACK_FMT)  # 11

# ====== CONFIG ======
# Alcance esperado PELO FIRMWARE (mantenha 4095 para 12-bit; mude para 255 se 8-bit)
FW_ABS_MAX = 4095
# ====================

@dataclass
class Movement:
    message_id: int
    robot_id: int
    v1: int
    v2: int
    v3: int
    v4: int  # mantido por compatibilidade; para 3 rodas, envie 0
    kicker: bool

    def pack(self) -> bytes:
        return struct.pack(PACK_FMT,
                           self.message_id & 0xFF,
                           self.robot_id & 0xFF,
                           int(self.v1),
                           int(self.v2),
                           int(self.v3),
                           int(self.v4),
                           bool(self.kicker))

    @staticmethod
    def clamp(x: float, abs_max: int = FW_ABS_MAX) -> int:
        x = int(round(x))
        return max(-abs_max, min(abs_max, x))

    @staticmethod
    def scale_from_source(x: float, src_abs_max: float, dst_abs_max: int = FW_ABS_MAX) -> int:
        """
        Converte um valor |x|<=src_abs_max para a escala do firmware (|.|<=dst_abs_max).
        Útil se sua estratégia produz -1..1, m/s normalizado, ou ±255.
        """
        if src_abs_max <= 0:
            return 0
        return Movement.clamp(x * (dst_abs_max / float(src_abs_max)), abs_max=dst_abs_max)
    
    
