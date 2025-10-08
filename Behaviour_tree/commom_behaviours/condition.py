import logging
from typing import Any

import py_trees
from py_trees.common import Status

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D
from utils.defines import (MAX_SHOOT_DISTANCE)
import Behaviour_tree.helpers.visiblidade_gol as vis_gol

positions_values = BlackboardKeys.Values.Positions
_bb = Blackboard_Manager.get_instance()
_ws = World_State.get_object()

# =======================================================================================#
#                                     IMPLEMENTADOS                                     #
# =======================================================================================#

logger = logging.getLogger(__name__)


class TeamHasBall(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está com adversário (TODO)
    """

    def __init__(self, name: str = "TeamHasBall"):
        super().__init__(name)

    def initialise(self) -> None:
        """Reseta/atualiza contexto no início da verificação."""
        ...

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}"):
            logger.debug(f"{self.name} - SUCCESS")
            return py_trees.common.Status.SUCCESS
        logger.debug(f"{self.name} - FAILURE")
        return py_trees.common.Status.FAILURE


class FoesHaveBall(py_trees.behaviour.Behaviour):
    """
    Verifica se a bola está com adversário (TODO)
    """

    def __init__(self, name: str = "FoesHaveBall"):
        super().__init__(name)

    def initialise(self) -> None:
        """Reseta/atualiza contexto no início da verificação."""
        ...

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}"):
            logger.debug(f"{self.name} - SUCCESS")
            return py_trees.common.Status.SUCCESS
        logger.debug(f"{self.name} - FAILURE")
        return py_trees.common.Status.FAILURE


class HasBall(py_trees.behaviour.Behaviour):

    def __init__(self, robot: Bob, name: str = "HasBall"):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs: Any) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(
            f"{self.robot.state.robot_id.name}{BlackboardKeys.Flags.BallMotion.HAS_BALL}"
        ):
            logger.debug(f"{self.name}-{self.robot.robot_id.name} - SUCCESS")
            return py_trees.common.Status.SUCCESS
        logger.debug(f"{self.name}-{self.robot.robot_id.name} - FAILURE")
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
            return py_trees.common.Status.RUNNING
        return py_trees.common.Status.FAILURE


class BolaSegura(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "BolaSegura"):
        self._ws = World_State.get_object()
        self.robot = robot
        super().__init__(name)

    def setup(self, **kwargs):
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL):
            logger.debug(f"{self.name} - FAILURE FOES com bola")
            return py_trees.common.Status.FAILURE

        ball = self._ws.get_ball_position()
        robots = self._ws.get_all_robot_position()
        robot_pos = self.robot.state.position
        for robot in robots:
            if ball.distance_to(robot) < ball.distance_to(robot_pos):
                logger.debug(f"{self.name} - FAILURE OUTRO ROBO MAIS PROX")
                return py_trees.common.Status.FAILURE
        logger.debug(f"{self.name} - SUCCESS")
        return py_trees.common.Status.SUCCESS


class ReceiverUnmarked(py_trees.behaviour.Behaviour):

    def __init__(self, name: str = "Receiver_Unmarked"):
        super().__init__(name)

    def setup(self, **kwargs):
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        if _bb.get(f"{BlackboardKeys.Flags.TeamContext.UNMARKED_RECEIVER}"):
            return py_trees.common.Status.RUNNING

        return py_trees.common.Status.FAILURE


###class rotation_done(py_trees.behaviour.Behaviour):#rotacionar em relaçaom ao alvo para realizar o passe
# DENTRO DO NO DE AÇAO CHOOSE WHO TO PASS
## def __init__(self, Robot:Bob, name: str = "Rotation_done"):
##   super().__init__(name)
# self.robot = Robot
# self.bb = Blackboard_Manager.get_instance()

# def update(self) -> py_trees.common.Status:
# if self.bb.get(
#   f"{self.robot.robot_id}{positions_values.rotation_done}"
#  ):
# return py_trees.common.Status.SUCCESS
#   return py_trees.common.Status.RUNNING

########PASSE#########################   ACIMAAAAAAAA


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
    
class Goal_visibility(py_trees.behaviour.Behaviour):
    def __init__(
      self,
      attacker: Bob,
      name: str = "Goal_visibility"
  ):
      super().__init__(name)
      self.attacker = attacker

def setup(self, **kwargs: Any) -> None:
      if self.attacker is None:
          raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
      return super().setup(**kwargs)
def update(self) -> py_trees.common.Status:
      obstacles_pose = _ws.get_all_robot_position()
      attacker_id = self.attacker.robot_id.value   # Transforma de enum para int
      attacker_pose = _ws.get_team_robot_pose(attacker_id)
      goal_center = _pos_helper.get_goal_center()
      x_goal = goal_center.x
    
      if(vis_gol.max_range_of_visibility(obstacles_pose, attacker_pose, x_goal)):
          return py_trees.common.Status.SUCCESS
      return py_trees.common.Status.FAILURE




class Goal_distance(py_trees.behaviour.Behaviour):
  def __init__(
      self,
      attacker: Bob,
      name: str = "Goal_distance",
  ):
      super().__init__(name)
      self.attacker = attacker

def setup(self, **kwargs: Any) -> None:
      if self.attacker is None:
          raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
      return super().setup(**kwargs)

def update(self) -> py_trees.common.Status:
      attacker_id = self.attacker.robot_id.value   # Transforma de enum para int
      attacker_pose = _ws.get_team_robot_pose(attacker_id)

      goal_center = _pos_helper.get_goal_center()
      x_goal = goal_center.x

      distance_to_goal = attacker_pose.distance_to(Pose2D(x_goal, goal_center.y))
      if(distance_to_goal <= MAX_SHOOT_DISTANCE):
          return py_trees.common.Status.SUCCESS
      return py_trees.common.Status.FAILURE

