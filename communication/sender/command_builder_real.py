from communication.sender.messages import Movement, MSG_ID_CMD, FW_ABS_MAX

class CommandBuilderReal:
    """
    Constrói o pacote Movement para o robô REAL.
    Por padrão, assume que os valores recebidos já estão na escala do firmware (±4095).
    Se sua origem estiver em outra escala (ex.: ±255, ±1.0), use os parâmetros src_abs_max_*.
    """
    def __init__(self, robot_id: int = 1, src_abs_max: float | None = None):
        """
        src_abs_max: se informado, os w1/w2/w3 recebidos serão reescalados de ±src_abs_max para ±FW_ABS_MAX.
        Ex.: src_abs_max=255 (manual antigo 8-bit) -> reescala para 12-bit.
             src_abs_max=1.0 (valores normalizados) -> reescala para 12-bit.
        """
        self.robot_id = robot_id
        self.src_abs_max = src_abs_max  # None => já está em ±FW_ABS_MAX

    def _to_fw_scale(self, x: float) -> int:
        if self.src_abs_max is None:
            # Já está em ±FW_ABS_MAX
            return Movement.clamp(x, abs_max=FW_ABS_MAX)
        # Reescalar de ±src_abs_max para ±FW_ABS_MAX
        return Movement.scale_from_source(x, src_abs_max=self.src_abs_max, dst_abs_max=FW_ABS_MAX)

    def build(self, w1: float, w2: float, w3: float, kicker: bool = False) -> Movement:
        return Movement(
            message_id=MSG_ID_CMD,
            robot_id=self.robot_id,
            v1=self._to_fw_scale(w1),
            v2=self._to_fw_scale(w2),
            v3=self._to_fw_scale(w3),
            v4=0,  # robô de 3 rodas
            kicker=bool(kicker)
        )
