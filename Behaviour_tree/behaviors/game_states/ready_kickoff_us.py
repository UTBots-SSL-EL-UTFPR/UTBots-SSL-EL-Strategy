from .behaviour_base import Behaviour

class ReadyKickoffUsBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ready_kickoff_us")

    def on_enter(self, prev_state: str | None) -> None:
        # so alinhar/posicionar; chute bloqueado ate normal_start
        self.permits.update({"move": True, "orient": True, "kick": False, "place_ball_robot": None})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
