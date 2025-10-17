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
from Behaviour_tree.helpers.positioning_helper import PositioningHelper

from ..core.event_callbacks import BlackboardKeys
from ..core.World_State import TeamID, World_State

# from utils.defines import BALL_DISTANCE_FOR_SHOOT

positions = BlackboardKeys.Values.Positions
import time
from typing import Optional, Tuple

import py_trees as pt

import Behaviour_tree.helpers as hp
import Behaviour_tree.helpers.visiblidade_gol as vis_gol
from Behaviour_tree.helpers.motion_helper import MotionHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.defines import BALL_DISTANCE_FOR_KICK
from utils.pose2D import Pose2D, RoleType

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
        timeout_s: float = 5,
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
        self._bb.set(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}",
            False,
        )
        self._bb.set(self.target_reached_key, False)
        logger.debug("MOVE")

    def update(self) -> pt.common.Status:
        """
        Empurra o robô enquanto não atingiu o alvo.
        Depende do Blackboard para saber se o alvo foi alcançado (`target_reached_key`).

        :returns: SUCCESS quando alvo alcançado; RUNNING durante o deslocamento; FAILURE em erro/timeout.
        :rtype: pt.common.Status
        """
        if self.robot is None:
            return pt.common.Status.FAILURE
        logger.debug(f"{self.robot.state.target_position} - target")
        logger.debug(f"{self.robot.state.position}")

        if bool(self._bb.get(self.target_reached_key)):
            logging.debug(f"{self.name} - {self.robot.robot_id} SUCCESS")
            return pt.common.Status.SUCCESS

        if not getattr(self.robot.state, "target_position", None):
            logger.debug(
                f"{self.name} - {self.robot.robot_id.name} - FAILURE  TARGET NONE"
            )
            return pt.common.Status.FAILURE

        if (time.time() - self._t0) > self.timeout_s:
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE  TIMEOUT")
            return pt.common.Status.FAILURE

        if self._bb.get(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}"
        ):
            logger.debug(
                f"{self.name} - {self.robot.robot_id.name} - FAILURE  ROBOT STUCK"
            )
            return pt.common.Status.FAILURE
        logger.debug(f"{self.name} - {self.robot.robot_id.name} - RUNNING")
        self.robot.fast_movement()
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
    por enquanto assume estar em boa pos para tal, mas deve ser verificado
    """

    def __init__(self, robot: Bob, name: str = "RecuperarBola"):
        super().__init__(name)
        self._bb = py_trees.blackboard.Blackboard()
        self.robot = robot
        self.team_has_ball = f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}"
        self.foes_have_ball = f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}"

    def setup(self, **kwargs) -> None:
        logger.debug(f"setup {self.name}")
        self._bb.set(self.team_has_ball, False)
        self._bb.set(self.foes_have_ball, False)
        return super().setup(**kwargs)

    def update(self) -> py_trees.common.Status:
        """vai atras da bola"""
        if self._bb.get(self.team_has_ball):
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE TEAM")
            return py_trees.common.Status.FAILURE
        if self._bb.get(self.foes_have_ball):
            logger.debug(f"{self.name} - {self.robot.robot_id.name} - FAILURE FOES")
            return py_trees.common.Status.FAILURE
        self.robot.set_new_target(hp.StrategyHelper.get_ball_recovery_position())
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
        logger.debug(f"{self.name} - SUCCESS")

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
        self.ph = PositioningHelper.get_object()

    def setup(self, **kwargs):
        logger.debug(f"setup {self.name}")
        return super().setup(**kwargs)

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return py_trees.common.Status.FAILURE

        passer_pos = self.robot.state.position
        passer_id = self.robot.robot_id
        opp_pos = self.world_state.get_all_foes_position()

        allied_robots = []

        for team_id in TeamID:
            if team_id.value == passer_id.value:
                continue
            robot_pose = self.world_state.get_team_robot_pose(team_id.value)
            if robot_pose is not None:
                allied_robots.append({"id": team_id, "pose": robot_pose})

        forward_teammates = []
        for teammate in allied_robots:
            if teammate["id"].value != passer_id.value:
                if teammate["pose"].x > passer_pos.x:
                    forward_teammates.append(teammate)

        if not forward_teammates:
            logger.debug(
                f"[{self.name}] - FAILURE Nenhum companheiro à frente para passar."
            )
            return py_trees.common.Status.FAILURE

        best_target = None
        min_distance = float("inf")

        for candidate in forward_teammates:
            candidate_pos = candidate["pose"]

            if self.ph.is_path_clear(passer_pos, candidate_pos, opp_pos):
                distance = (
                    (passer_pos.x - candidate_pos.x) ** 2
                    + (passer_pos.y - candidate_pos.y) ** 2
                ) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    best_target = candidate

        if best_target is not None:
            self.bb.set("pass_target_id", best_target["id"])
            self.bb.set("pass_target_pos", best_target["pose"])
            logger.debug(f" {self.name} - SUCCESS")
            return py_trees.common.Status.SUCCESS
        else:
            logger.debug(
                f"[{self.name}] - Retornando FAILURE. ompanheiros à frente, mas sem caminho livre"
            )
            return py_trees.common.Status.FAILURE


    
class Calculate_linear_target_pass(pt.behaviour.Behaviour):
    def __init__(self, kicker: Bob, name: str = "Calculate_kick_target"):
        super().__init__(name)
        self.kicker = kicker
        self._bb = Blackboard_Manager.get_instance()
        self.desired_angle = 0.0

    def setup(self, **kwargs):
        if self.kicker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self._bb.set(f"{self.kicker.robot_id.name}_team_kick", True)
        self.kicker.state.role = RoleType.KICKER

    def update(self) -> pt.common.Status:
        if self.kicker is None or self.kicker.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        kicker_pose = self.kicker.state.position
        target_pose = self._bb.get("pass_target_pos")
        obstacles_pose = _ws.get_all_robot_position()
        obstacles_pose.remove(kicker_pose)
        ball_pose = _ws.get_ball_position()

        # Cálculo do ângulo
        desired_angle = _pos_helper.get_passer_orientation(
            kicker_pose, target_pose
        )

        # Cálculo o ponto alvo de alinhamento
        x_target = ball_pose.x - BALL_DISTANCE_FOR_KICK * math.cos(desired_angle)
        y_target = ball_pose.y - BALL_DISTANCE_FOR_KICK * math.sin(desired_angle)

        # Settando o target e a trajetória
        self.kicker.state.set_target_position(
            (Pose2D)(x_target, y_target, self.kicker.state.position.theta)
        )
        self.kicker.state.path = MotionHelper.find_shortest_path(
            kicker_pose, self.kicker.state.target_position, obstacles_pose, ball_pose
        )

        return pt.common.Status.SUCCESS

class Calculate_angular_target_pass(pt.behaviour.Behaviour):
    def __init__(self, kicker: Bob, name: str = "Calculate_angular_target"):
        super().__init__(name)
        self.kicker = kicker
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.kicker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        pass

    def update(self) -> pt.common.Status:
        if self.kicker is None or self.kicker.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        kicker_pose = self.kicker.state.position
        target_pose = self.bb.get("pass_target_pos")
        
        
        # Cálculo do ângulo
        desired_angle = _pos_helper.get_passer_orientation(
            kicker_pose, target_pose
        )

        # Settando o target
        self.bb.set(f"{self.kicker.state.target_position}", None)
        self.kicker.set_new_target(Pose2D(kicker_pose.x, kicker_pose.y, desired_angle))

        return pt.common.Status.SUCCESS

class Angular_align_pass(pt.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Angular_align", tolerance=0.10):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()
        self.tolerance = tolerance
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self._bb.set(f"{self.robot.robot_id.name}_team_kick", True)

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        robot_id = self.robot.robot_id.value  # Transforma de enum para int
        robot_pose = _ws.get_team_robot_pose(robot_id)
        target_pos = self._bb.get("pass_target_pos")
        obstacles_pose = _ws.get_all_robot_position()
        obstacles_pose.remove(robot_pose)

        # Cálculo do ângulo
        desired_angle = _pos_helper.get_passer_orientation(
            robot_pose, target_pos
        )

        # Verifica se o movimento foi feito
        if hp.PositioningHelper.is_aligned(
            robot_pose,
            desired_angle,
            tolerance=self.tolerance,
        ):
            return pt.common.Status.SUCCESS

        # Retorna failure se o robo estiver travado em um mesmo movimento há muito tempo

        # Realiza o movimento
        rotate_cmd = self.robot.rotate()

        if self._bb.get(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}"
        ):
            logger.debug(
                f"{self.name} - {self.robot.robot_id.name} - FAILURE  ROBOT STUCK"
            )
            return pt.common.Status.FAILURE

        if not rotate_cmd:
            return pt.common.Status.FAILURE
        else:
            return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status):
        pass
    
    



class ExecutePass(py_trees.behaviour.Behaviour):
    """
    Nó que executa o passe, lendo a posição do alvo no Blackboard e
    enviando o comando de chute ao robô passador.
    """

    def __init__(self, robot: Bob, name):
        super().__init__(name)
        self.robot = robot
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] Robô não definido no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        pass

    def update(self) -> pt.common.Status:

        if self.robot is None or self.robot.state is None:

            return pt.common.Status.FAILURE

        target_pos = self.bb.get("pass_target_pos")
        if target_pos is None:
            return pt.common.Status.FAILURE

        # Envia comando de chute
        try:
            self.robot.kick_ball()
            logging.info(f"{self.robot.robot_id} executou passe para {target_pos}")
            self.bb.set("pass_target_pos", None)
            self.bb.set("pass_target_id", None)

            return pt.common.Status.SUCCESS
        except Exception as e:
            logging.error(f"Erro ao executar passe: {e}")
            return pt.common.Status.FAILURE

    def terminate(self, new_status: pt.common.Status):
        pass


# =+==============================++++++==================++++++=================+++++=============#

# --------------------------------------------------------------------------------------- #
#                                      CHUTE                                              #
# --------------------------------------------------------------------------------------- #


# Calcula o ponto aonde o robô deve ir para poder chutar no gol (específico do chute no gol)
class Calculate_linear_target(pt.behaviour.Behaviour):
    def __init__(self, kicker: Bob, name: str = "Calculate_kick_target"):
        super().__init__(name)
        self.kicker = kicker
        self._bb = Blackboard_Manager.get_instance()
        self.desired_angle = 0.0

    def setup(self, **kwargs):
        if self.kicker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self._bb.set(f"{self.kicker.robot_id.name}_team_kick", True)
        self.kicker.state.role = RoleType.KICKER

    def update(self) -> pt.common.Status:
        if self.kicker is None or self.kicker.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        kicker_pose = self.kicker.state.position
        goal_pose = _pos_helper.get_goal_center()
        obstacles_pose = obstacles_pose = _ws.get_all_obstacles_position(kicker_pose)
        ball_pose = _ws.get_ball_position()

        # Cálculo do ângulo
        desired_angle = _pos_helper.middle_goal_visibility_range(
            kicker_pose, goal_pose, obstacles_pose
        )

        # Cálculo o ponto alvo de alinhamento
        x_target = int(ball_pose.x - BALL_DISTANCE_FOR_KICK * math.cos(desired_angle))
        y_target = int(ball_pose.y - BALL_DISTANCE_FOR_KICK * math.sin(desired_angle))

        # Settando o target e a trajetória
        self.bb.set(f"{self.kicker.state.target_position}", None)
        self.kicker.set_new_target(
            (Pose2D)(x_target, y_target, self.kicker.state.position.theta)
        )
        self.kicker.state.path = MotionHelper.find_shortest_path(
            kicker_pose, target, obstacles_pose, ball_pose
        )
        return pt.common.Status.SUCCESS


# Calcula o angulo que o robo deve estar para chutar o gol (cálculo do ângulo específico para o chute no gol)
class Calculate_angular_target(pt.behaviour.Behaviour):
    def __init__(self, kicker: Bob, name: str = "Calculate_angular_target"):
        super().__init__(name)
        self.kicker = kicker
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.kicker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        pass

    def update(self) -> pt.common.Status:
        if self.kicker is None or self.kicker.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        kicker_pose = self.kicker.state.position
        goal_pose = _pos_helper.get_goal_center()
        obstacles_pose = _ws.get_all_obstacles_position(kicker_pose)

        # Cálculo do ângulo
        desired_angle = _pos_helper.middle_goal_visibility_range(
            kicker_pose, goal_pose, obstacles_pose
        )

        # Settando o target
        self.bb.set(f"{self.kicker.state.target_position}", None)
        self.kicker.set_new_target(Pose2D(kicker_pose.x, kicker_pose.y, desired_angle))
      
        
        return pt.common.Status.SUCCESS


# Faz o alinhamento angular com o gol (pode ser usado por qualquer bob que quer girar para um target já settado)
class Angular_align(pt.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "Angular_align", tolerance=0.10):
        super().__init__(name)
        self.robot = robot
        self._bb = Blackboard_Manager.get_instance()
        self.tolerance = tolerance
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self._bb.set(f"{self.robot.robot_id.name}_team_kick", True)

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        # Inicializações que eu vou precisar
        robot_pose = self.robot.state.position
        goal_pose = _pos_helper.get_goal_center()
        obstacles_pose = _ws.get_all_obstacles_position(robot_pose)

        # Cálculo do ângulo
        desired_angle = _pos_helper.middle_goal_visibility_range(
            robot_pose, goal_pose, obstacles_pose
        )

        # Verifica se o movimento foi feito
        if hp.PositioningHelper.is_aligned(
            robot_pose,
            desired_angle,
            tolerance=self.tolerance,
        ):
            return pt.common.Status.SUCCESS

        # Retorna failure se o robo estiver travado em um mesmo movimento há muito tempo

        # Realiza o movimento
        rotate_cmd = self.robot.rotate()

        if self._bb.get(
            f"{self.robot.robot_id.name}{BlackboardKeys.Flags.Navigation.IS_STUCK}"
        ):
            logger.debug(
                f"{self.name} - {self.robot.robot_id.name} - FAILURE  ROBOT STUCK"
            )
            return pt.common.Status.FAILURE

        if not rotate_cmd:
            return pt.common.Status.FAILURE
        else:
            return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status):
        self.bb.set(f"{self.kicker.state.target_position}", None)


class Shoot_to_goal(pt.behaviour.Behaviour):
    def __init__(
        self,
        kicker: Bob,
        name: str = "Shoot_to_goal",
    ):
        super().__init__(name)
        self.kicker = kicker
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.kicker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def update(self) -> pt.common.Status:
        if self.kicker is None or self.kicker.state is None:
            return pt.common.Status.FAILURE

        kick_cmd = self.kicker.kick_ball()

        if not kick_cmd:
            return pt.common.Status.FAILURE
        else:
            return pt.common.Status.SUCCESS

    def terminate(self, new_status: pt.common.Status):
        self._bb.set(f"{self.kicker.robot_id.name}_team_kick", False)
        self.kicker.state.reset()
