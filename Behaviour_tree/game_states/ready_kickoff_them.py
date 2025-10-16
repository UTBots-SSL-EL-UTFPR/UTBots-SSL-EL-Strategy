from .behaviour_base import Behaviour

class ReadyKickoffThemBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ready_kickoff_them")

    def on_enter(self, prev_state: str | None) -> None:
        self.permits.update({"move": True, "orient": True, "kick": False})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
