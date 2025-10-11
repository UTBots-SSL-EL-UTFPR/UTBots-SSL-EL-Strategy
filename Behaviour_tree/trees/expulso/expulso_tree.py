"""
Expulso tree: checa se o robô foi expulso (TODO) e, se sim, vai para fora do campo.
"""
from __future__ import annotations

import py_trees as pt
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from utils.defines import FIELD_X_MIN, FIELD_X_MAX, FIELD_Y_MIN, FIELD_Y_MAX


def get_expulso_tree(robot: Bob) -> pt.behaviour.Behaviour:
    is_expulsed = IsExpelled(robot)
    go_off_field = GoOffField(robot)
    return pt.composites.Sequence(name="ExpulsoTree", memory=False, children=[is_expulsed, go_off_field])


class IsExpelled(pt.behaviour.Behaviour):
    """TODO: implementar checagem real de expulsão (cartão, regra, árbitro)."""
    def __init__(self, robot: Bob, name: str = "IsExpelled"):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()

    def update(self) -> pt.common.Status:
        # TODO: checar flag no blackboard ou mensagem do árbitro
        return pt.common.Status.SUCCESS


class GoOffField(pt.behaviour.Behaviour):
    """Leva o robô ao ponto mais próximo fora do campo, a partir da sua posição atual."""
    def __init__(self, robot: Bob, name: str = "GoOffField"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        pos = self.robot.state.position if self.robot and self.robot.state else Pose2D(0, 0)
        x, y = pos.x, pos.y if hasattr(pos, 'x') else pos[0], pos[1]  # compatível com tupla ou Pose2D

        # Candidatos fora do campo (um pouco além dos limites)
        candidates = [
            Pose2D(FIELD_X_MIN - 200, y),  # esquerda
            Pose2D(FIELD_X_MAX + 200, y),  # direita
            Pose2D(x, FIELD_Y_MIN - 200),  # baixo
            Pose2D(x, FIELD_Y_MAX + 200),  # cima
        ]
        # Escolhe o mais perto
        target = min(candidates, key=lambda p: p.distance_to(pos))

        self.robot.set_new_target(target)
        self.robot.fast_movement()
        return pt.common.Status.SUCCESS
