# Behaviour_tree/core/game_state_analyzer.py
from utils.defines import FIELD_INVERTED_SIDE

from . import event_callbacks as callbacks
from .World_State import TeamID, World_State

POSSESSION_THRESHOLD = 350.0


class GameStateAnalyzer:
    """
    Analisa os dados brutos do World_State e atualiza o Blackboard com
    flags de alto nível que descrevem o contexto do jogo.
    """

    def __init__(self):
        self.ws = World_State.get_object()
        self.last_possession_state = "NONE"
        # CORREÇÃO: Adiciona a variável para rastrear o ID de quem tem a posse
        self.last_possessor_id: TeamID | None = None

    def update(self):
        """
        Executa a análise completa a cada ciclo do jogo.
        """
        # 1. Limpa as flags do ciclo anterior para garantir uma análise limpa
        callbacks.set_ball_in_defensive_half(False)

        # 2. Analisa a situação atual e ativa as flags necessárias
        self._analyze_ball_position()
        self._analyze_possession()

    def _analyze_ball_position(self):
        """Verifica se a bola está no nosso campo de defesa."""
        ball_pos = self.ws.get_ball_position()

        if ball_pos and (
            FIELD_INVERTED_SIDE
            and ball_pos.x > 0
            or not FIELD_INVERTED_SIDE
            and ball_pos.x < 0
        ):
            callbacks.set_ball_in_defensive_half(True)

    def _analyze_possession(self):
        """
        Verifica qual time tem a posse da bola e dispara eventos apenas
        quando o estado da posse muda, garantindo consistência.
        """
        ball_pos = self.ws.get_ball_position()
        foes = self.ws.get_all_foes_position()
        allies_with_ids = [
            (id_enum, pos)
            for id_enum in TeamID
            if (pos := self.ws.get_team_robot_pose(id_enum.value))
        ]
        current_possession, possessor_id = "NONE", None

        if ball_pos:
            # Encontra o aliado e adversário mais próximos da bola
            closest_ally_enum, closest_ally_pos = min(
                allies_with_ids,
                key=lambda i: i[1].distance_to(ball_pos),
                default=(None, None),
            )
            ally_dist = (
                closest_ally_pos.distance_to(ball_pos)
                if closest_ally_pos
                else float("inf")
            )

            closest_foe = (
                min(foes, key=lambda f: f.distance_to(ball_pos), default=None)
                if foes
                else None
            )
            foe_dist = (
                closest_foe.distance_to(ball_pos) if closest_foe else float("inf")
            )

            # Decide quem tem a posse
            if ally_dist <= foe_dist and ally_dist < POSSESSION_THRESHOLD:
                current_possession, possessor_id = "ALLY", closest_ally_enum
            elif foe_dist < ally_dist and foe_dist < POSSESSION_THRESHOLD:
                current_possession = "FOE"

        # Se o estado da posse mudou, notifica o sistema
        if current_possession != self.last_possession_state:
            if current_possession == "ALLY" and possessor_id:
                callbacks.team_got_ball_posetion(possessor_id.name)
                if self.last_possession_state == "FOE":
                    callbacks.foes_lost_ball_posetion("unknown_foe")

            elif current_possession == "FOE":
                callbacks.foes_got_ball_posetion("unknown_foe")
                if self.last_possession_state == "ALLY" and self.last_possessor_id:
                    callbacks.lost_ball_posetion(self.last_possessor_id.name)

            elif current_possession == "NONE":
                if self.last_possession_state == "ALLY" and self.last_possessor_id:
                    callbacks.lost_ball_posetion(self.last_possessor_id.name)
                elif self.last_possession_state == "FOE":
                    callbacks.foes_lost_ball_posetion("unknown_foe")

        # Atualiza o estado para o próximo ciclo
        self.last_possession_state = current_possession
        self.last_possessor_id = possessor_id if current_possession == "ALLY" else None
