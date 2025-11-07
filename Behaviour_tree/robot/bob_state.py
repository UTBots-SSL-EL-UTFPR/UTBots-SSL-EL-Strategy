from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from SSL_configuration.configuration import Configuration
from utils.pose2D import Pose2D, RoleType


class Bob_State:
    """Estado dinâmico do robô (posição, velocidade, posse, quadrante e role)."""

    def __init__(self):

        self._position: Pose2D = Pose2D(3333, 3333)
        self._velocity: Pose2D = Pose2D()

        self._path: list[Pose2D] = []
        self.fast_mov = 0
        self._path_index = 0

        self._target_position: Pose2D | None = Pose2D()
        self.target_theta: float | None = 0

        self.active_function = None
        self.current_command: str = "None"
        self.role: RoleType | None = None

        self.ball_visible = False
        self.has_ball = False
        self.position_rept = 0

    def reset(self):
        self._position = Pose2D(3333, 3333)
        self._velocity = Pose2D()
        self._path.clear()
        self._path_index = 0
        self._target_position = None
        self.role = None
        self.has_ball = False

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: Pose2D | None):
        if value is not None:
            self._position = value

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value: Pose2D | None):
        if value is not None:
            self._velocity = value

    @property
    def path(self) -> list[Pose2D]:
        """Lista de pontos da trajetória."""
        return self._path

    @path.setter
    def path(self, new_path: list[Pose2D]):
        """Define uma nova trajetória e reseta o índice."""
        if not isinstance(new_path, list):
            raise TypeError("path deve ser uma lista de Pose2D")
        self._path = new_path
        self._path_index = 0

    def add_path_point(self, target: Pose2D):
        """Adiciona um ponto ao final da trajetória."""
        self._path.append(target)

    @property
    def target_position(self) -> Pose2D | None:
        """Retorna o alvo atual (último ponto da trajetória)."""
        if self._path:
            return self._path[-1]
        return self._target_position

    @target_position.setter
    def target_position(self, target: Pose2D | None):
        """Define uma nova posição-alvo, limpando o caminho atual."""
        self._path.clear()
        self._path_index = 0
        self._target_position = target
        if target:
            self._path.append(target)
