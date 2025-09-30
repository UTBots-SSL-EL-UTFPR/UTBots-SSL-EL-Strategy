import logging
from typing import Any

import py_trees
from py_trees.common import Status

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

positions_values = BlackboardKeys.Values.Positions
_bb = Blackboard_Manager.get_instance()
_pos_helper = PositioningHelper.get_object()

# =======================================================================================#
#                                     IMPLEMENTADOS                                     #
# =======================================================================================#

logger = logging.getLogger(__name__)


class TeamHasBall(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está com adversário (TODO)
    """

    def __init__(self, name: str = "IsBallFree"):
        super().__init__(name)

    def initialise(self) -> None:
        """Reseta/atualiza contexto no início da verificação."""
        ...

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}"):
            logger.debug("time nao tem a posse de bola")

            return py_trees.common.Status.SUCCESS
        logger.debug("time possui a bola")
        return py_trees.common.Status.FAILURE


class FoesHaveBall(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está com adversário (TODO)
    """

    def __init__(self, name: str = "IsBallFree"):
        super().__init__(name)

    def initialise(self) -> None:
        """Reseta/atualiza contexto no início da verificação."""
        ...

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}"):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class HasBall(py_trees.behaviour.Behaviour):

    def __init__(self, robot: Bob, name: str = "Has_ball"):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs: Any) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(
            f"{self.robot.state.robot_id.name}{BlackboardKeys.Flags.BallMotion.HAS_BALL}"
        ):
            logger.debug(f" robo {self.robot.robot_id.name} tem posse de bola")
            return py_trees.common.Status.SUCCESS
        logger.debug(f" robo {self.robot.robot_id.name} não esta com a bola")
        return py_trees.common.Status.FAILURE


# =======================================================================================#
#                                         x                                             #
# =======================================================================================#


class ValidLine(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Valid_Line"):
        super().__init__(name)

    def setup(self, **kwargs):
        return super().setup(**kwargs)


    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.TeamContext.VALID_LINE}"):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class ReceiverUnmarked(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Receiver_Unmarked"):
        super().__init__(name)

    def setup(self, **kwargs):
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.TeamContext.UNMARKED_RECEIVER}"):
            return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE




class BallVisible(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, robot: Bob):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs: Any) -> None:
        if self.robot:
            print("setup")

    def update(self) -> Status:
        if not self.robot or not self.robot.state:
            return py_trees.common.Status.FAILURE

        if _bb.get(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.BallMotion.BALL_VISIBLE}"
        ):
            return py_trees.common.Status.SUCCESS
        pos = _bb.get(f"{self.robot.robot_id.name}{positions_values.POS_BALL_VISIBLE}")

        if isinstance(pos, Pose2D):
            self.robot.adicionar_ponto_trajetoria(pos)
        else:
            print("blackboard com valor nulo no lugar de pos2d par mov desmarque")
        return py_trees.common.Status.FAILURE


class Teamkick(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Team_kick"):
        super().__init__(name)

    def setup(self, **kwargs: Any) -> None:
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.KickActions.TEAM_KICK}"):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE
