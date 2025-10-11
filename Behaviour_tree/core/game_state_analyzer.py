# Behaviour_tree/core/game_state_analyzer.py
from .World_State import World_State, TeamID
from . import event_callbacks as callbacks
from utils.defines import FIELD_INVERTED_SIDE

POSSESSION_THRESHOLD = 350.0
DANGEROUS_BALL_SPEED = 500.0

class GameStateAnalyzer:
    def __init__(self):
        self.ws = World_State.get_object()
        self.last_possession_state = 'NONE'
        self.last_possessor_id: TeamID | None = None

    def update(self):
        """
        Executa a análise completa do estado do jogo a cada ciclo.
        A ordem (limpar -> analisar) é crucial para a consistência.
        """
        # ============================================================================== #
        # CORREÇÃO: Limpa o estado das flags no início de cada ciclo.
        # ============================================================================== #
        self._reset_defensive_flags()

        # Agora, analisa a situação e ativa apenas as flags necessárias.
        self._analyze_possession()
        self._analyze_threats()

    def _reset_defensive_flags(self):
        """Reseta todas as flags de defesa para False."""
        callbacks.set_ball_is_a_threat(False)
        callbacks.set_ball_in_defensive_half(False)
        callbacks.set_opponent_in_danger_zone(False)

    def _analyze_threats(self):
        """Analisa a situação e LIGA as flags de ameaça, se aplicável."""
        ball_pos = self.ws.get_ball_position()
        ball_vel = self.ws.get_ball_velocity()
        
        # Análise 1: Ameaça de chute forte
        if ball_vel and (FIELD_INVERTED_SIDE and ball_vel.x > DANGEROUS_BALL_SPEED or not FIELD_INVERTED_SIDE and ball_vel.x < -DANGEROUS_BALL_SPEED):
            callbacks.set_ball_is_a_threat(True)

        # Análise 2: Bola no nosso campo
        if ball_pos and (FIELD_INVERTED_SIDE and ball_pos.x > 0 or not FIELD_INVERTED_SIDE and ball_pos.x < 0):
            callbacks.set_ball_in_defensive_half(True)

        # Análise 3: Oponente com a bola em zona de perigo
        if self.last_possession_state == 'FOE':
            opponents = self.ws.get_all_foes_position()
            if ball_pos and opponents:
                try:
                    opp_with_ball = min(opponents, key=lambda opp: opp.distance_to(ball_pos))
                    danger_zone_x_min, danger_zone_x_max = (0, 2250) if FIELD_INVERTED_SIDE else (-2250, 0)
                    DANGER_ZONE_Y_MIN, DANGER_ZONE_Y_MAX = -1500, 1500
                    if (danger_zone_x_min < opp_with_ball.x < danger_zone_x_max and DANGER_ZONE_Y_MIN < opp_with_ball.y < DANGER_ZONE_Y_MAX):
                        callbacks.set_opponent_in_danger_zone(True)
                except (ValueError, TypeError):
                    pass
        
    def _analyze_possession(self):
        # A versão completa e estável da análise de posse
        ball_pos = self.ws.get_ball_position()
        foes = self.ws.get_all_foes_position()
        allies_with_ids = [(id_enum, pos) for id_enum in TeamID if (pos := self.ws.get_team_robot_pose(id_enum.value))]
        current_possession, possessor_id = 'NONE', None

        if ball_pos:
            closest_ally_enum, closest_ally_pos = min(allies_with_ids, key=lambda i: i[1].distance_to(ball_pos), default=(None, None))
            ally_dist = closest_ally_pos.distance_to(ball_pos) if closest_ally_pos else float('inf')
            closest_foe = min(foes, key=lambda f: f.distance_to(ball_pos), default=None)
            foe_dist = closest_foe.distance_to(ball_pos) if closest_foe else float('inf')

            if ally_dist <= foe_dist and ally_dist < POSSESSION_THRESHOLD:
                current_possession, possessor_id = 'ALLY', closest_ally_enum
            elif foe_dist < ally_dist and foe_dist < POSSESSION_THRESHOLD:
                current_possession = 'FOE'

        if current_possession != self.last_possession_state:
            if current_possession == 'ALLY' and possessor_id:
                callbacks.team_got_ball_posetion(possessor_id.name)
                if self.last_possession_state == 'FOE': callbacks.foes_lost_ball_posetion("unknown_foe")
            elif current_possession == 'FOE':
                callbacks.foes_got_ball_posetion("unknown_foe")
                if self.last_possession_state == 'ALLY' and self.last_possessor_id: callbacks.lost_ball_posetion(self.last_possessor_id.name)
            elif current_possession == 'NONE':
                if self.last_possession_state == 'ALLY' and self.last_possessor_id: callbacks.lost_ball_posetion(self.last_possessor_id.name)
                elif self.last_possession_state == 'FOE': callbacks.foes_lost_ball_posetion("unknown_foe")
        
        self.last_possession_state = current_possession
        self.last_possessor_id = possessor_id if current_possession == 'ALLY' else None