# Behaviour_tree/trees/defender/defender_conditions.py
import py_trees
from Behaviour_tree.core.World_State import World_State

# Limite de velocidade para considerar um chute perigoso (ajuste conforme necessário)
DANGEROUS_BALL_SPEED_X = -500  # Velocidade negativa em X (em direção ao nosso gol)

class IsBallMovingFastTowardsGoal(py_trees.behaviour.Behaviour):
    """Verifica se a bola é uma ameaça de gol iminente."""
    def __init__(self, name: str = "Ameaça de Gol Iminente?"):
        super().__init__(name)
        self.ws = World_State.get_object()

    def update(self) -> py_trees.common.Status:
        ball_vel = self.ws.get_ball_velocity()
        # Considera perigoso se a velocidade em X na direção do nosso gol for alta
        if ball_vel and ball_vel.x < DANGEROUS_BALL_SPEED_X:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsOpponentWithBallInDangerZone(py_trees.behaviour.Behaviour):
    """Verifica se um oponente com a bola está em uma zona de chute perigosa."""
    def __init__(self, name: str = "Oponente Perigoso?"):
        super().__init__(name)
        self.ws = World_State.get_object()

    def update(self) -> py_trees.common.Status:
        # TODO: Implementar a lógica para verificar se algum oponente
        # próximo da bola está dentro da sua "zona de perigo"
        # Por enquanto, vamos retornar FAILURE para não ativar este ramo.
        return py_trees.common.Status.FAILURE

class IsBallInDefensiveHalf(py_trees.behaviour.Behaviour):
    """Verifica se a bola está no nosso lado do campo."""
    def __init__(self, name: str = "Bola no Campo de Defesa?"):
        super().__init__(name)
        self.ws = World_State.get_object()

    def update(self) -> py_trees.common.Status:
        ball_pos = self.ws.get_ball_position()
        if ball_pos and ball_pos.x < 0: # Assumindo que nosso gol está em X negativo
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE