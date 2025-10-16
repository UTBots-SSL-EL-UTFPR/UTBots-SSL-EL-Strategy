from .behaviour_base import Behaviour

class RunningBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="running")

    def on_enter(self, prev_state: str | None) -> None:
        # liberar arvore completa, libera tudo
        self.permits.update({"move": True, "orient": True, "kick": True})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
