# Behaviour_tree/behaviors/game_states/stop.py
from .behaviour_base import Behaviour

class StopBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="stop")

    def on_enter(self, prev_state: str | None) -> None:
        # permitir apenas posicionamento/orientacao leve; chute bloqueado
        self.permits.update({"move": True, "orient": True, "kick": False, "place_ball_robot": None})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        # se quiser, aqui voce pode aferir limites (ex: dist >= 0.5m da bola) e
        # re publicar flags caso precise 
        pass
