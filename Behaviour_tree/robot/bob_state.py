from ..core.World_State import World_State, RobotID
from ..core.blackboard import Blackboard_Manager

from .all_bob_states import AllBobs_State

from utils.pose2D import Pose2D

from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    ATTACK_QUADRANTS,
    MIDFIELD_QUADRANTS,
    DEFENSE_QUADRANTS,
    GOALKEEPER_ZONE,
    BALL_POSSESSION_DISTANCE,
)


class Bob_State:
    """Estado dinâmico do robô (posição, velocidade, posse, quadrante e role)."""
    def __init__(self, robot_id: RobotID):
        self.blackboard = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.position: Pose2D = Pose2D()
        self.velocity: Pose2D = Pose2D()
        self.target_position: Pose2D = Pose2D()
        self.active_function = None
        self.current_command = None
        self.has_ball = False
        self.world_state = World_State()  # Singleton do campo
        self.quadrant_index: int | None = None
        self.role: RoleType | None = None

        # Registrar no singleton agregador
        self.get_all_bobs = AllBobs_State.get_instance()
        self.get_all_bobs.register(self)

    def update(self):
        self.ball = self.world_state.get_ball_position()  
        self.position = self.world_state.get_team_robot_pose(self.robot_id.value)
        self.velocity = self.world_state.get_team_robot_velocity(self.robot_id.value)

        #self.has_ball = self.world_state.check_possession(self.robot_id.value)
        self.quadrant_index = self.get_quadrant()

    # =================== Setters básicos ===================
    def set_position(self, position: Pose2D):
        """Define manualmente a posição e recalcula quadrante e role."""
        self.position = position
        self.quadrant_index = self.get_quadrant()

    def set_velocity(self, velocity: Pose2D):
        """Atualiza o vetor de velocidade (vx, vy)."""
        self.velocity = velocity

    def set_orientation(self, angle: float):
        """Define a orientação atual do robô."""
        self.orientation = angle

    def set_target_position(self, position: Pose2D):
        """Define uma posição alvo (goal) para planejamento de movimento."""
        self.target_position = position

    def reset(self):
        """Restaura o estado para valores padrão (limpa alvo, role e quadrante)."""
        self.position = Pose2D()
        self.velocity = Pose2D()
        self.target_position = Pose2D()
        self.active_function = None
        self.current_command = None
        self.has_ball = False
        self.quadrant_index = None
        self.role = None

    # =================== Métricas / consultas ===================
    def check_ball_possession(self) -> bool:
        ball_position = self.world_state.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE
        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False

    def get_quadrant(self) -> int:
        """Calcula e retorna o índice (1..12) do quadrante atual ou 0 se fora do campo."""
        x, y = self.position
        for i, (x_min, x_max, y_min, y_max) in enumerate(ALL_QUADRANTS, 1):
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return i
        return 0  # fora do campo

    def get_role(self) -> RoleType | None:
        """Retorna o RoleType atual; recalcula se ainda não definido."""
        if self.role is None:
            self.role = self._infer_role_from_position(*self.position)
        return self.role

    # =================== Getters simples para agregador ===================
    def get_position(self)-> Pose2D:
        return self.position

    def get_velocity(self)-> Pose2D:
        return self.velocity
    
    # =================== Internos de classificação ===================
    def _is_attack_quadrant(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa ofensiva."""
        return q in ATTACK_QUADRANTS

    def _is_midfield_quadrant(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa de meio-campo."""
        return q in MIDFIELD_QUADRANTS

    def _is_defense_quadrant(self, q: Quadrant_type) -> bool:
        """True se o quadrante pertence à faixa defensiva."""
        return q in DEFENSE_QUADRANTS

    def _is_in_goalkeeper_zone(self, x: float, y: float) -> bool:
        """Retorna True se (x,y) estiver dentro da zona retangular reservada ao goleiro."""
        xmin, xmax, ymin, ymax = GOALKEEPER_ZONE
        return xmin <= x <= xmax and ymin <= y <= ymax

    def _get_quadrant_type_by_index(self, idx: int):
        """Converte índice num Enum Quadrant_type ou None se inválido."""
        try:
            return Quadrant_type(idx)
        except ValueError:
            return None

    def _get_role_by_quadrant(self, q: Quadrant_type, x: float | None = None, y: float | None = None) -> RoleType:
        """Determina o RoleType base usando agrupamentos e zona do goleiro."""
        if x is not None and y is not None and self._is_in_goalkeeper_zone(x, y):
            return RoleType.GOALKEEPER
        if self._is_attack_quadrant(q):
            return RoleType.ATTACK
        if self._is_midfield_quadrant(q):
            return RoleType.MIDFIELD
        if self._is_defense_quadrant(q):
            return RoleType.DEFENSE
        return RoleType.SUPPORT

    def _infer_role_from_position(self, x: float, y: float) -> RoleType:
        """Inferência completa: encontra quadrante e converte para RoleType apropriado."""
        for i, (xmin, xmax, ymin, ymax) in enumerate(ALL_QUADRANTS, 1):
            if xmin <= x <= xmax and ymin <= y <= ymax:
                q = self._get_quadrant_type_by_index(i)
                return self._get_role_by_quadrant(q, x, y) if q else RoleType.SUPPORT
        return RoleType.SUPPORT
    
    
    