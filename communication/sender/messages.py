import struct
from dataclasses import dataclass

#IDs 
MSG_ID_CMD  = 100
MSG_ID_PING = 101

# protocolo binario do ian (11 bytes)
PACK_FMT = '<BBhhhh?'
PACK_SIZE = struct.calcsize(PACK_FMT)  # 11

# ====== CONFIG ======
# PWM do firmware é 12 bits
FW_ABS_MAX = 4095
# ====================

@dataclass
class Movement:
    message_id: int
    robot_id: int
    v1: int
    v2: int
    v3: int
    v4: int  
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
        converte um valor |x|<=src_abs_max para a escala do pwm do firmware (|.|<=dst_abs_max).
        """
        if src_abs_max <= 0:
            return 0
        return Movement.clamp(x * (dst_abs_max / float(src_abs_max)), abs_max=dst_abs_max)
    
    