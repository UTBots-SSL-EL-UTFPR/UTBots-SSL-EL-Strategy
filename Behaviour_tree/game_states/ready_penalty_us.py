from .behaviour_base import Behaviour

class ReadyPenaltyUsBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ready_penalty_us")

    def on_enter(self, prev_state: str | None) -> None:
        # tipicamente so o batedor se move; mas por enquanto mantemos gating generico
        self.permits.update({"move": True, "orient": True, "kick": False})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
