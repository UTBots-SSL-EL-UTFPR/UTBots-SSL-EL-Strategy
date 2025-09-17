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
from Behaviour_tree.core.event_callbacks import BB_flags_and_values

from ...core.event_callbacks import BB_flags_and_values
from ...core.World_State import RobotID, World_State

navigation_flags = BB_flags_and_values.Flags.motion.navigation
positions = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags
import time
from typing import Optional, Tuple

import py_trees as pt

team_flags = BB_flags_and_values.Flags.Team_Flags
from ...positioning import positioning_helper as Positioning_helper


from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.robot.bob import Bob

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
        name: str = "MOVE",
        robot=None,
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

        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.target_reached_key = (
            f"{self.robot.robot_id.name}{navigation_flags.target_reached}"
        )

    def initialise(self) -> None:
        if self.robot is None or self.robot.state is None:
            return

        self._t0 = time.time()
        self._last_move_ts = self._t0
        self._stall_ticks = 0
        self._bb.set(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}", False)  # type: ignore

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
            logging.debug(f"{self.robot.robot_id} -> TARGET REACHED")
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

        if self._bb.get(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}"):
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
        name: str = "Receive_pass",
        robot=None,
    ):
        super().__init__(name=name)
        self.robot: Bob | None = robot
        self._bb = Blackboard_Manager.get_instance()

        self.receive_key: str
        self.pos_pass_key: str = f"{positions.pos_pass_target}"

    def setup(self, **kwargs) -> None:
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.receive_key = (
            f"{self.robot.robot_id.name}{team_flags.kick_actions.team_pass}"
        )

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
            logger.debug(f"{self.robot.robot_id} nao esta recebendo passe")
            return pt.common.Status.FAILURE

        target = self._bb.get(self.pos_pass_key)
        if target is None:
            logger.warning("pos de passe nula")
            return pt.common.Status.FAILURE

        pose_target = Positioning_helper.compute_pose_facing_goal(target)

        self.robot.adicionar_ponto_trajetoria(pose_target)

        self._bb.set(self.receive_key, False)
        self._bb.set(self.pos_pass_key, None)

        logger.debug(f"indo pegar passe -> {pose_target}")

        return pt.common.Status.SUCCESS


class Rebound_position(pt.behaviour.Behaviour):
    """
    se posiciona de maneira a receber um rebote
    """

    def __init__(self, name: str = "Receive_pass", robot=None):
        super().__init__(name=name)
        self.robot: Bob | None = robot
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")

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
        if not self._bb.get(f"{team_flags.kick_actions.team_kick}"):
            logger.debug("nao é team kick")
            return pt.common.Status.FAILURE

        target_pose = Positioning_helper.calculate_rebound_position(
            self.robot.state.position
        )
        self.robot.adicionar_ponto_trajetoria(target_pose)
        logger.debug(f"indo rebotar -> {target_pose}")
        return pt.common.Status.SUCCESS


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
        return super().setup(**kwargs)

    def update(self)->pt.common.Status:

        if self.robot is None or self.robot.state is None:
            return py_trees.common.Status.FAILURE   
        
        target_pos_found = None
        target_id_found  = None

        if self.robot.robot_id == 2:
            target0 = RobotID.Kamiji
            target1 = RobotID.Defender
            min_distance = 1000000

            for robot_id_enum in [target0, target1]:
                pos = self.world_state.get_team_robot_pose(robot_id_enum)
                if pos is not None:
                    distance = ((self.robot.state.position.x - pos.x)**2 + (self.robot.state.position.y - pos.y)**2)**0.5
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

        # Verificação sem considerar oponentes
        if Positioning_helper.are_pass_orientations_aligned(
            passer_pose,
            receiver_pose,
            goal_pose,
            opponents=[],
            tolerance_deg=self.tolerance,
        ):
            return pt.common.Status.SUCCESS

        # Ângulo ideal receptor
        desired_receiver_angle = Positioning_helper.get_best_pass_orientation(
            passer_pose, receiver_pose, goal_pose, opponents=[]
        )
        # Ângulo ideal passador (olhando pro receptor)
        desired_passer_angle = math.atan2(
            receiver_pose.y - passer_pose.y, receiver_pose.x - passer_pose.x
        )

        # Ajustar passador
        angle_diff_passer = (desired_passer_angle - passer_pose.theta + math.pi) % (
            2 * math.pi
        ) - math.pi
        if abs(angle_diff_passer) > self.tolerance:
            self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", angle_diff_passer)

        # Ajustar receptor
        angle_diff_receiver = (
            desired_receiver_angle - receiver_pose.theta + math.pi
        ) % (2 * math.pi) - math.pi
        if abs(angle_diff_receiver) > self.tolerance:
            self.bb.set(
                f"{self.receiver.robot_id.name}_cmd_rotation", angle_diff_receiver
            )

        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status):
        self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", 0.0)
        self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", 0.0)
