from .behaviour_base import Behaviour

class BallPlacementUsBehaviour(Behaviour):
    def __init__(self) -> None:
        super().__init__(state_name="ball_placement_us")

    def on_enter(self, prev_state: str | None) -> None:
        # so um robo (futuro: definir pelo blackboard) podera tocar a bola
        self.permits.update({"move": True, "orient": True, "kick": False})
        super().on_enter(prev_state)

    def update(self, dt: float = 0.0) -> None:
        # futuro: validar sucesso de placement; por enquanto so mantem flags
        pass
