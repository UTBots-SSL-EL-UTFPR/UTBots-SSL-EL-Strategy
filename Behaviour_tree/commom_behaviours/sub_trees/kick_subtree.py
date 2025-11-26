# kick subtree.py
import logging
import time

import py_trees

import Behaviour_tree.helpers as hp
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.bob import Bob

from ..condition import HasBall

logger = logging.getLogger(__name__)
_bb = Blackboard_Manager.get_instance()


def getKickPose(id):
    ws = World_State.get_object()
    ball = ws.get_ball_position()
    ops = ws.get_all_robot_position(id)
    Hpos = hp.positioning_helper.PositioningHelper.get_object()
    target = Hpos.find_most_open_spot_on_enemy_goal(ball, ops)
    if not target:
        return None
    margin = 150  # alterar para ver distancia
    x = hp.FieldHelper.get_enemy_goal_center().x
    sign = x < 0
    margin = margin if sign else -margin
    robot_pose = hp.GeometryHelper.calculate_point_on_line(ball, target, margin)

    robot_pose.theta = hp.GeometryHelper.calculate_angle_between_points(ball, target)
    return robot_pose


import logging
import time

import py_trees

from SSL_configuration.configuration import Configuration

logger = logging.getLogger(__name__)


class PrecisionMove(py_trees.behaviour.Behaviour):
    """Move com precisão até (x, y) e opcionalmente theta, com timeout e detecção de travamento."""

    def __init__(self, path: str, name: str = "PrecisionMove", timeout_s: float = 5.0):
        super().__init__(name)
        self.path = path
        self.timeout_s = float(timeout_s)
        self._t0: float = 0.0
        self._cfg = Configuration.getObject()

    def setup(self, **kwargs) -> None:
        logger.debug("%s.setup()", self.name)
        return super().setup(**kwargs)

    def initialise(self) -> None:
        self._t0 = time.monotonic()
        logger.debug("%s.initialise()", self.name)

    def _arrived_xy(self, robot: Bob) -> bool:
        thresh_xy = 12
        target = robot.state.target_position
        if target is None:
            return False
        return target.distance_to(robot.state.position) <= thresh_xy

    def _arrived_theta(self, robot: Bob) -> bool:
        tol_theta = 0.05
        if not (pos := robot.state.target_position):
            return True
        tgt_theta = pos.theta
        if tgt_theta is None:
            return True

        return abs(tgt_theta - robot.state.position.theta) <= tol_theta

    def update(self) -> py_trees.common.Status:
        robot = _bb.get(self.path)
        if robot is None or not isinstance(robot, Bob):
            logger.debug(
                "%s - FAILURE: robot não encontrado em '%s'", self.name, self.path
            )
            return py_trees.common.Status.FAILURE

        target = robot.state.target_position
        if target is None:
            logger.debug(
                "%s - %s - FAILURE: target ausente", self.name, robot.robot_id.name
            )
            return py_trees.common.Status.FAILURE

        if (time.monotonic() - self._t0) > self.timeout_s:
            logger.debug(
                "%s - %s - TIMEOUT (%.2fs)",
                self.name,
                robot.robot_id.name,
                self.timeout_s,
            )
            return py_trees.common.Status.SUCCESS

        if self._arrived_xy(robot) and self._arrived_theta(robot):
            logger.debug(
                "%s - %s - SUCCESS (alvo: %s)", self.name, robot.robot_id.name, target
            )
            robot.state.target_theta = None
            return py_trees.common.Status.SUCCESS

        logger.debug(
            "%s - %s - RUNNING (pos=%s -> tgt=%s)",
            self.name,
            robot.robot_id.name,
            robot.state.position,
            target,
        )
        robot.precision_movement()
        return py_trees.common.Status.RUNNING


class AproachBall(py_trees.behaviour.Behaviour):
    """
    calcula super posição muito proxima
    """

    def __init__(self, path: str, name: str = "AproachBall"):
        super().__init__(name)
        self.path = path

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        pass

    def update(self) -> py_trees.common.Status:
        robot: Bob | None = _bb.get(self.path)
        if robot is None:
            logger.debug(f"{self.name} - FAILURE not bob")
            return py_trees.common.Status.FAILURE
        target = getKickPose(robot.robot_id)
        if not target:
            logger.debug(f"{self.name} - FAILURE not target")
            return py_trees.common.Status.SUCCESS
        print(robot.state.position)
        robot.set_new_target_position(target)
        logger.debug(
            f"{self.name} estou em {robot.state.position} e  preciso chegar em {robot.state.target_position} -- SUCCESS"
        )
        return py_trees.common.Status.SUCCESS


class PrepareKick(py_trees.behaviour.Behaviour):
    def __init__(
        self,
        path: str,
        name: str = "pseudochutemovunicodocaralhosuper",
        timeout_s: float = 5,
    ):
        super().__init__(name)
        self.path = path
        self._t0: float = 0.0
        self.timeout_s: float = timeout_s

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        self.initpose = World_State.get_object().get_ball_position()
        print(self.name)

    def update(self) -> py_trees.common.Status:
        robot: Bob | None = _bb.get(self.path)
        if robot is None:
            return py_trees.common.Status.FAILURE
        if not _bb.get(f"{robot.robot_id.name}{BlackboardKeys.HAS_BALL}"):
            logger.debug("saiu do chute")
            return py_trees.common.Status.SUCCESS
        pose = World_State.get_object().get_ball_position()
        robotPose = robot.state.position
        if abs(pose.x) - abs(self.initpose.x) > 5:
            return py_trees.common.Status.SUCCESS
        Z = -hp.FieldHelper.position_behind(15)
        pose = hp.GeometryHelper.displace_from_target_along(robotPose, pose, Z)
        logger.debug(f"{self.name} -- RUNNING -- {pose}")
        robot.set_new_target_position(pose)
        robot.fast_movement()
        return py_trees.common.Status.RUNNING


class Kick(py_trees.behaviour.Behaviour):
    def __init__(
        self,
        path: str,
        name: str = "pseudochutemovunicodocaralhosuper",
        timeout_s: float = 5,
    ):
        super().__init__(name)
        self.path = path

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        pass

    def update(self) -> py_trees.common.Status:
        robot: Bob | None = _bb.get(self.path)
        if robot is None:
            return py_trees.common.Status.FAILURE
        logger.debug
        robot.kick_ball()
        return py_trees.common.Status.SUCCESS


def get_kick_subtree(path: str) -> py_trees.composites.Sequence:
    # TODO
    has_ball = HasBall(path)
    app_ball = AproachBall(path)
    spp_kick = PrepareKick(path)
    pres_move = PrecisionMove(path)
    kick = Kick(path)
    aproach_subtree = py_trees.composites.Sequence(
        "arvore movimento para chute", True, children=[has_ball, app_ball, pres_move]
    )
    chutechute = py_trees.composites.Sequence("chute", False, children=[spp_kick, kick])
    kick_subtree = py_trees.composites.Sequence(
        "arvore de chute", True, children=[aproach_subtree, chutechute]
    )
    kick_subtree.setup()
    return kick_subtree
