"""
Stop tree: verifica condição de stop (TODO) e, se verdadeiro, para o robô.
"""
from __future__ import annotations

import py_trees as pt
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.robot.bob import Bob


def get_stop_tree(robot: Bob) -> pt.behaviour.Behaviour:
    """Retorna uma árvore: IsStopCondition -> StopRobot."""
    is_stop = IsStopCondition(robot)
    stop_robot = StopRobot(robot)
    return pt.composites.Sequence(name="StopTree", memory=False, children=[is_stop, stop_robot])


class IsStopCondition(pt.behaviour.Behaviour):
    """TODO: Implementar checagem real (árbitro, segurança, etc.)."""
    def __init__(self, robot: Bob, name: str = "IsStopCondition"):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()

    def update(self) -> pt.common.Status:
        # TODO: colocar lógica real
        return pt.common.Status.SUCCESS


class StopRobot(pt.behaviour.Behaviour):
    """Para o robô enviando velocidades zero, ou usando robot.stop() se existir."""
    def __init__(self, robot: Bob, name: str = "StopRobot"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> pt.common.Status:
        if hasattr(self.robot, "stop") and callable(getattr(self.robot, "stop")):
            try:
                self.robot.stop()
                return pt.common.Status.SUCCESS
            except Exception:
                pass
        try:
            # fallback: zera rodas
            self.robot.cmd_builder.command_robots(
                id=self.robot.robot_id.value,
                wheelsspeed=True,
                wheel1=0.0,
                wheel2=0.0,
                wheel3=0.0,
                wheel4=0.0,
            )
            self.robot.cmd = self.robot.cmd_builder.build()
            self.robot.cmd_sender.send(self.robot.cmd)
            return pt.common.Status.SUCCESS
        except Exception:
            return pt.common.Status.FAILURE
