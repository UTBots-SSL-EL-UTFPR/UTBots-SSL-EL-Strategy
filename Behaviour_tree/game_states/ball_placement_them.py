from .behaviour_base import Behaviour

class BallPlacementThemBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ball_placement_them")

    def on_enter(self, prev_state: str | None) -> None:
        # nao interferir; somente afastamento e posicionamento passivo
        self.permits.update({"move": True, "orient": True, "kick": False, "place_ball_robot": None})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        pass
