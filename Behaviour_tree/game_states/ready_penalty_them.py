from .behaviour_base import Behaviour

class ReadyPenaltyThemBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ready_penalty_them")

    def on_enter(self, prev_state: str | None) -> None:
        self.permits.update({"move": True, "orient": True, "kick": False, "place_ball_robot": None})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
