from .behaviour_base import Behaviour

class HaltBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="halt")

    def on_enter(self, prev_state: str | None) -> None:
        # parar tudo: sem movimento, sem chute
        self.permits.update({"move": False, "orient": False, "kick": False})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        # nada a fazer por tick, manter flags
        pass
