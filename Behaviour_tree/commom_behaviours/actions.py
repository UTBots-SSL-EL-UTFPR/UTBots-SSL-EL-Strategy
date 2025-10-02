"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""

from __future__ import annotations

import logging
import math
import time
from time import sleep

import py_trees

from Behaviour_tree.core import event_callbacks as callbacks
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys

from ..core.event_callbacks import BlackboardKeys
from ..core.World_State import RobotID, World_State

positions = BlackboardKeys.Values.Positions
import time
from typing import Optional, Tuple

import py_trees as pt

import Behaviour_tree.helpers as hp
from Behaviour_tree.robot.bob import Bob
from utils.pose2D import Pose2D

import Behaviour_tree.helpers.visiblidade_gol as vis_gol
from Behaviour_tree.helpers.positioning_helper import PositioningHelper

_pos_helper = PositioningHelper.get_object()
_ws = World_State.get_object()

# ---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
# ---------------------------------------------------------------------------------------#
logger = logging.getLogger(__name__)


class Move_node(pt.behaviour.Behaviour):
    """
    Nó de movimento genérico: empurra o robô  até robot.state.target_position (path inteiro)

    :param name: Nome do nó.
    :type name: str
    :param robot: Instância do robô (Bob).
    :type robot: Bob | None
    :param timeout_s: Tempo máximo (segundos) para tentar alcançar o alvo antes de retornar FAILURE.
    :type timeout_s: float
    """

    def __init__(
        self,
        robot: Bob,
        name: str = "MOVE",
        timeout_s: float = 15,
    ):
        super().__init__(name=name)
        self.robot: Bob | None = robot
        self._bb = Blackboard_Manager.get_instance()

        self.target_reached_key = ""
        self.timeout_s = timeout_s

        self._t0: float = 0.0
        self._last_move_ts: float = 0.0
        self._stall_ticks: int = 0
        self._max_stall_ticks: int = 30

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.target_reached_key = f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.TARGET_REACHED}"

        self._bb.set(self.target_reached_key, False)

    def initialise(self) -> None:
        if self.robot is None or self.robot.state is None:
            return

        self._t0 = time.time()
        self._last_move_ts = self._t0
        self._stall_ticks = 0
        self._bb.set(f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}", False)  # type: ignore

        self._bb.set(self.target_reached_key, False)

    def update(self) -> pt.common.Status:
        """
        Empurra o robô enquanto não atingiu o alvo.
        Depende do Blackboard para saber se o alvo foi alcançado (`target_reached_key`).

        :returns: SUCCESS quando alvo alcançado; RUNNING durante o deslocamento; FAILURE em erro/timeout.
        :rtype: pt.common.Status
        """
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        if bool(self._bb.get(self.target_reached_key)):
            logging.debug(f"{self.name}-{self.robot.robot_id} SUCCESS")
            return pt.common.Status.SUCCESS

        if not getattr(self.robot.state, "target_position", None):
            return pt.common.Status.FAILURE

        try:
            self.robot.fast_movement()
        except Exception as exc:
            return pt.common.Status.FAILURE

        if (time.time() - self._t0) > self.timeout_s:
            logging.warning(f"{self.robot.robot_id} -> MOVE TIMEOUT")
            return pt.common.Status.FAILURE

        if self._bb.get(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}"
        ):
            logging.debug(f"{self.robot.robot_id} -> ROBOT STUCK")
            return pt.common.Status.FAILURE
        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status) -> None:
        if self.robot is None or self.robot.state is None:
            return

        self.robot.state.target_position = None

        try:
            callbacks.target_reset(self.robot.robot_id.name)
        except Exception:
            pass


# -------------------------------------------------------------------------------------------------#


# -------------------------------------------------------------------------------------------------#
class Receive_pass(pt.behaviour.Behaviour):
    """
    Se for pra ele, intercepta a bola e 'vira' para o gol, preparando o alvo de recepção.
    - Lê no BB: positions.pos_pass_target e a flag de passe destinado a este robô.
    - Converte o alvo em (x, y, theta~0.0) e chama compute_pose_facing_goal(target)
    - Adiciona a Pose2D resultante como ponto de trajetória
    """

    def __init__(
        self,
        robot: Bob,
        name: str = "Receive_pass",
    ):
        super().__init__(name=name)
        self.robot: Bob = robot
        self._bb = Blackboard_Manager.get_instance()
        self.receive_key: str

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.receive_key = (
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.KickActions.TEAM_PASS}"
        )
        self.pos_pass_key: str = f"{BlackboardKeys.Values.Positions.POS_PASS_TARGET}"
        self._bb.set(self.receive_key, False)
        self._bb.set(self.pos_pass_key, False)

    def initialise(self) -> None:
        pass

    def update(self) -> pt.common.Status:
        """
        Verifica se deve preparar o movimento de receber passe,
        calcula a Pose2D alvo apontando para o centro do gol e
        adiciona na trajetória do robô. Retorna SUCCESS ao preparar.
        """

        if self.robot is None or getattr(self.robot, "state", None) is None:
            return pt.common.Status.FAILURE

        passe = self._bb.get(self.receive_key)
        if not passe:
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE")
            return pt.common.Status.FAILURE

        target = self._bb.get(self.pos_pass_key)
        if target is None:
            logger.warning("pos de passe nula")
            return pt.common.Status.FAILURE

        pose_target = hp.PositioningHelper.compute_pose_facing_goal(target)

        self.robot.adicionar_ponto_trajetoria(pose_target)

        self._bb.set(self.receive_key, False)
        self._bb.set(self.pos_pass_key, None)

        logger.debug(f"{self.name} - {self.robot.robot_id.name} - SUCCESS")
        self.robot.state.current_command = self.name

        return pt.common.Status.SUCCESS


class Rebound_position(pt.behaviour.Behaviour):
    """
    se posiciona de maneira a receber um rebote
    """

    def __init__(self, robot: Bob, name: str = "Rebound_position"):
        super().__init__(name=name)
        self.robot: Bob = robot
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.team_kick_key = f"{BlackboardKeys.Flags.KickActions.TEAM_KICK}"
        self._bb.set(self.team_kick_key, False)

    def initialise(self) -> None:
        pass

    def update(self) -> pt.common.Status:
        """
        Verifica se deve preparar o movimento de receber passe,
        calcula a Pose2D alvo apontando para o centro do gol e
        adiciona na trajetória do robô. Retorna SUCCESS ao preparar.
        """
        if self.robot is None or self.robot.state is None:
            logger.warning("robo NONE")
            return pt.common.Status.FAILURE
        if not self._bb.get(self.team_kick_key):
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE")
            return pt.common.Status.FAILURE

        target_pose = hp.PositioningHelper.calculate_rebound_position(
            self.robot.state.position
        )
        self.robot.adicionar_ponto_trajetoria(target_pose)
        logger.debug(f"{self.name} - {self.robot.robot_id.name} - SUCCESS")
        self.robot.state.current_command = self.name

        return pt.common.Status.SUCCESS


class RecuperarBola(py_trees.behaviour.Behaviour):
    """
    decide se ira tentar recuperar a bola, faz isso se a bola nao estiver com ninguem do time
    se der falha, entao a bola é confirmada como em nossa posse
    ja da um followball inteligente, mirando ficar atras da bola
    TODO testar com mov willian
    por enquanto assume estar em boa pos para tal, mas deve ser verificado
    """

    def __init__(self, robot: Bob, name: str = "RecuperarBola"):
        super().__init__(name)
        self._bb = py_trees.blackboard.Blackboard()
        self.robot = robot
        self.team_has_ball = f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}"

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        self._bb.set(self.team_has_ball, False)

        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """vai atras da bola"""
        if not self._bb.get(self.team_has_ball):
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE")
            return py_trees.common.Status.FAILURE
        self.robot.state.target_position = (
            hp.StrategyHelper.get_ball_recovery_position()
        )
        self.robot.state.current_command = self.name
        logger.debug(f"{self.name} - {self.robot.robot_id.name} - SUCCESS")
        return py_trees.common.Status.SUCCESS


class MovimentoUnico(py_trees.behaviour.Behaviour):
    """
    envia um movimento e retorna Sucess
    """

    def __init__(self, robot: Bob, name: str = "MovimentoUnico"):
        super().__init__(name)
        self.robot = robot

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def initialise(self) -> None:
        logger.debug("movimento unitario")

    def update(self) -> py_trees.common.Status:
        self.robot.fast_movement()
        self.robot.state.current_command = self.name

        return py_trees.common.Status.SUCCESS


# ---------------------------------------------------------------------------------------#
#                                      PASSE                                            A#
# ---------------------------------------------------------------------------------------#


class Choose_who_to_pass(py_trees.behaviour.Behaviour):

    def __init__(self, Robot: Bob, name):
        super().__init__(name)
        self.robot = Robot
        self.bb = Blackboard_Manager.get_instance()
        self.world_state = World_State.get_object()

    def setup(self, **kwargs):
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> pt.common.Status:

        if self.robot is None or self.robot.state is None:
            return py_trees.common.Status.FAILURE

        target_pos_found = None
        target_id_found = None

        if self.robot.robot_id == 2:
            target0 = RobotID.Kamiji
            target1 = RobotID.Defender
            min_distance = 1000

            for robot_id_enum in [target0, target1]:
                pos = self.world_state.get_team_robot_pose(robot_id_enum)
                if pos is not None:
                    distance = (
                        (self.robot.state.position.x - pos.x) ** 2
                        + (self.robot.state.position.y - pos.y) ** 2
                    ) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        target_pos_found = pos
                        target_id_found = robot_id_enum

        elif self.robot.robot_id == 1:
            target_id_found = RobotID.Kamiji
            target_pos_found = self.world_state.get_team_robot_pose(target_id_found)
        else:
            target_id_found = RobotID.Defender
            target_pos_found = self.world_state.get_team_robot_pose(target_id_found)

        if target_pos_found is not None and target_id_found is not None:
            self.bb.set("pass_target_id", target_id_found)
            self.bb.set("pass_target_pos", target_pos_found)
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


class Align_for_pass(pt.behaviour.Behaviour):
    """
    Nó que garante que passador e receptor estejam orientados corretamente.
    Se não estiverem, envia comandos de rotação até alinhar.
    """

    def __init__(
        self,
        passer: Bob,
        receiver: Bob,
        name: str = "Align_for_pass",
        tolerance: float = 0.15,
    ):
        super().__init__(name)
        self.passer = passer
        self.receiver = receiver
        self.tolerance = tolerance
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.passer is None or self.receiver is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", 0.0)
        self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", 0.0)

    def update(self) -> pt.common.Status:
        if (
            self.passer is None
            or self.receiver is None
            or self.passer.state is None
            or self.receiver.state is None
        ):
            return pt.common.Status.FAILURE

        passer_pose = self.passer.state.position
        receiver_pose = self.receiver.state.position
        goal_pose = self.bb.get("goal_pose")
        if not isinstance(goal_pose, Pose2D):
            return pt.common.Status.FAILURE
        # Checa alinhamento geral
        if hp.PositioningHelper.are_pass_orientations_aligned(
            passer_pose,
            receiver_pose,
            goal_pose,
            tolerance=self.tolerance,
        ):
            return pt.common.Status.SUCCESS

        # Ângulos desejados
        desired_receiver_angle = hp.PositioningHelper.get_best_pass_orientation(
            passer_pose, receiver_pose, goal_pose, opponents=[]
        )
        desired_passer_angle = hp.PositioningHelper.get_passer_orientation(
            passer_pose, receiver_pose
        )

        # Gera comandos (se necessário)
        cmd_passer = hp.PositioningHelper.get_rotation_command(
            passer_pose.theta, desired_passer_angle, self.tolerance
        )
        cmd_receiver = hp.PositioningHelper.get_rotation_command(
            receiver_pose.theta, desired_receiver_angle, self.tolerance
        )

        if cmd_passer is not None:
            self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", cmd_passer)
        if cmd_receiver is not None:
            self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", cmd_receiver)

        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status):
        self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", 0.0)
        self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", 0.0)


# =+==============================++++++==================++++++=================+++++=============#

# --------------------------------------------------------------------------------------- #
#                                      CHUTE                                              #
# --------------------------------------------------------------------------------------- #

class Align_for_shoot(pt.behaviour.Behaviour):
  def __init__(
      self,
      attacker: Bob,
      name: str = "Align_for_shoot",
      tolerance = 0.15
  ):
      super().__init__(name)
      self.attacker = attacker
      self.bb = Blackboard_Manager.get_instance()
      self.tolerance = tolerance


  def setup(self, **kwargs):
      if self.attacker is None:
          raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
      return super().setup(**kwargs)


  def initialise(self):
      self.bb.set(f"{self.attacker.robot_id.name}_team_kick", True)
      self.bb.set(f"{self.attacker.robot_id.name}_cmd_rotation", 0.0)


  def update(self) -> pt.common.Status:
      if (
          self.attacker is None
          or self.attacker.state is None
      ):
          return pt.common.Status.FAILURE
    
      attacker_pose = self.attacker.state.position
      goal_pose = _pos_helper.get_goal_center()
      obstacles_pose = _ws.get_all_robot_position()

      max_angle_visibility_field, min_angle_visibility_field = vis_gol.limits_of_visibility(obstacles_pose, attacker_pose, goal_pose)
      # Esse angulo é dado em relacação ao eixo x+ quando x_gol>0 e x- quando x_gol<0
      visArea_center_rad = (max_angle_visibility_field + min_angle_visibility_field) / 2
     
      if goal_pose.x < 0 :
          visArea_center_rad = (visArea_center_rad + math.pi)*-1

      if hp.PositioningHelper.is_aligned_to_goal(
            attacker_pose,
            visArea_center_rad,
            tolerance = self.tolerance,
        ):
            return pt.common.Status.SUCCESS

      rotate_cmd = self.attacker.rotate(visArea_center_rad)

      if not rotate_cmd:
          return pt.common.Status.FAILURE
      else:
          return pt.common.Status.RUNNING


  def terminate(self, new_status: pt.common.Status):
      self.bb.set(f"{self.attacker.robot_id.name}_cmd_rotation", 0.0)



class Shoot_to_goal(pt.behaviour.Behaviour):
  def __init__(
      self,
      attacker: Bob,
      name: str = "Shoot_to_goal",
  ):
      super().__init__(name)
      self.attacker = attacker
      self.bb = Blackboard_Manager.get_instance()


  def setup(self, **kwargs):
      if self.attacker is None:
          raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
      return super().setup(**kwargs)


  def initialise(self):
      self.bb.set(f"{self.attacker.robot_id.name}_cmd_rotation", 0.0)


  def update(self) -> pt.common.Status:
      if (
          self.attacker is None
          or self.attacker.state is None
      ):
          return pt.common.Status.FAILURE
     
      kick_cmd = self.attacker.kick_ball()


      if not kick_cmd:
          return pt.common.Status.FAILURE
      else:
          return pt.common.Status.SUCCESS
     
     
  def terminate(self, new_status: pt.common.Status):
      self.bb.set(f"{self.attacker.robot_id.name}_team_kick", False)