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

from utils.defines import BALL_DISTANCE_FOR_SHOOT

positions = BlackboardKeys.Values.Positions
import time
from typing import Optional, Tuple

import py_trees as pt

import Behaviour_tree.helpers as hp
import Behaviour_tree.helpers.visiblidade_gol as vis_gol
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.robot.bob import Bob
from utils.defines import BALL_DISTANCE_FOR_SHOOT
from utils.pose2D import Pose2D

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

        target_pos_found = None
        target_id_found = None
        opp_pos = self.world_state.get_all_foes_position()

        if self.robot.robot_id == 2:
            target0 = TeamID.Kamiji
            target1 = TeamID.Argenton
            min_distance = 1000

            for robot_id_enum in [target0, target1]:
                pos = self.world_state.get_team_robot_pose(robot_id_enum)
                if pos is not None:
                    distance = (
                        (self.robot.state.position.x - pos.x) ** 2
                        + (self.robot.state.position.y - pos.y) ** 2
                    ) ** 0.5
                    if distance < min_distance:
                        if(self.ph.is_path_clear(self.robot.state.position,pos,opp_pos)):
                            min_distance = distance
                            target_pos_found = pos
                            target_id_found = robot_id_enum

        elif self.robot.robot_id == 1:
            target_id_found = TeamID.Kamiji
            target_pos_found = self.world_state.get_team_robot_pose(target_id_found)
        else:
            target_id_found = TeamID.Argenton
            target_pos_found = self.world_state.get_team_robot_pose(target_id_found.value)

            
        if target_pos_found is not None and target_id_found is not None:
        
            self.bb.set("pass_target_id", target_id_found)
            self.bb.set("pass_target_pos", target_pos_found)
            logger.debug(f"{self.name}-{self.robot.robot_id.name} - SUCCESS")
            return py_trees.common.Status.SUCCESS
        else:
            logger.error(f"[{self.name}] Não foi possível encontrar um alvo para o passe. Retornando FAILURE.")
            return py_trees.common.Status.FAILURE

class Calculate_target(pt.behaviour.Behaviour):
    def __init__(
        self,
        attacker: Bob,
        name: str = "Calculate_kick_target"
    ):
        super().__init__(name)
        self.attacker = attacker
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.attacker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self.bb.set(f"{self.attacker.robot_id.name}_team_kick", True)

    def update(self) -> pt.common.Status:
     
        if (
        self.attacker is None
        or self.attacker.state is None
        ):
            return pt.common.Status.FAILURE

        
        target_pos = self.bb.get("pass_target_pos")
        if target_pos is None:
            logger.error(f"[{self.name}] Alvo de passe (pass_target_pos) é Nulo.")
            return pt.common.Status.FAILURE

      
        attacker_pose = self.attacker.state.position
        desired_angle = math.atan2(target_pos.y - attacker_pose.y, target_pos.x - attacker_pose.x)
        
      
        
        ball_pose = _ws.get_ball_position() 
        
        
        BALL_PASS_OFFSET = 0.1 # Valor de exemplo (ajuste conforme sua calibração)

        # O ponto de destino é logo ATRÁS da bola, alinhado com o ângulo de passe
        x_target = ball_pose.x - BALL_PASS_OFFSET * math.cos(desired_angle)
        y_target = ball_pose.y - BALL_PASS_OFFSET * math.sin(desired_angle)

        
        self.attacker.state.target_position = Pose2D(x_target, y_target, desired_angle)

        return pt.common.Status.SUCCESS

class Align(pt.behaviour.Behaviour):
    def __init__(
        self,
        attacker: Bob,
        name: str = "Align_for_shoot",
        tolerance_rad=0.15,
        tolerance_xy=30,
    ):
        super().__init__(name)
        self.attacker = attacker
        self.bb = Blackboard_Manager.get_instance()
        self.tolerance_rad = tolerance_rad
        self.tolerance_xy = tolerance_xy

    def setup(self, **kwargs):
        if self.attacker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self.bb.set(f"{self.attacker.robot_id.name}_cmd_movement", 0.0)

    def update(self) -> pt.common.Status:

      if (
          self.attacker is None
          or self.attacker.state is None
      ):
          return pt.common.Status.FAILURE
    
      # Realiza o movimento
      self.attacker.precision_movement()

      attacker_id = self.attacker.robot_id.value   # Transforma de enum para int
      attacker_pose = _ws.get_team_robot_pose(attacker_id)


      if self.attacker.state.target_reached:
          print("sucess")
          return pt.common.Status.SUCCESS

      else:
          print("running")
          return pt.common.Status.RUNNING


    def terminate(self, new_status: pt.common.Status):
      #self.bb.set(f"{self.attacker.robot_id.name}_cmd_movement", 0.0)
        ...


    
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
                self.robot.kick_ball(self.robot)
                logging.info(f"{self.robot.robot_id} executou passe para {target_pos}")
                # Limpa o alvo de passe no Blackboard
                self.bb.set("pass_target_pos", None)
                self.bb.set("pass_target_id", None)
                print ("AAAAAAAAAAAAAAAAA")
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
### TENTE SEMPRE USAR OS NOMES DEF EM CALLBACKS, PARA NÃO CORRER RISCO DE TROCAR LETRAS E QUEBRAR O COD
### SEMPRE QUE FOR ATT A TARGET DO BOB, CHAME A FUNÇÃO DELE QUE FAZ ISSO, O JEITO Q ELE SE MOVE FUNCIONA COMO
### UMA LISTA, ENTÃO PRECISAMOS RESETAR ELA SEMPRE
### msm coisa de como vc pega a pos do bob, usa bob.state.position
###  self.attacker.state.target_position -->  self.attacker.set_new_target()
### se não esta funcionado, eu diria q é devido a ele recalcular diversas vezes o movimento, tente fazer o seguinte:
### separe esse nó em 2, um para o mov e um para calc o angulo/pos
### coesão e desaclopamento!


class Calculate_target(pt.behaviour.Behaviour):
    def __init__(
        self,
        attacker: Bob,
        name: str = "Calculate_kick_target"
    ):
        super().__init__(name)
        self.attacker = attacker
        self.bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs):
        if self.attacker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self.bb.set(f"{self.attacker.robot_id.name}_team_kick", True)

    def update(self) -> pt.common.Status:
        if (
          self.attacker is None
          or self.attacker.state is None
      ):
          return pt.common.Status.FAILURE
    
        attacker_id = self.attacker.robot_id.value   # Transforma de enum para int
        attacker_pose = _ws.get_team_robot_pose(attacker_id)
        goal_pose = _pos_helper.get_goal_center()
        obstacles_pose = _ws.get_all_robot_position()
        obstacles_pose.remove(attacker_pose)


        max_angle_visibility_field, min_angle_visibility_field = vis_gol.limits_of_visibility(obstacles_pose, attacker_pose, goal_pose)
        # Esse angulo é dado em relacação ao eixo x+ quando x_gol>0 e x- quando x_gol<0
        visArea_center_rad = (max_angle_visibility_field + min_angle_visibility_field) / 2
     
        if goal_pose.x < 0 :    # Usa da propriedade dos ângulos opostos pelo vértice
            visArea_center_rad = (visArea_center_rad + math.pi)*-1
      
        ball_pose = _ws.get_ball_position()
        x_ball = ball_pose.x
        y_ball = ball_pose.y
      
        x_target = x_ball + BALL_DISTANCE_FOR_SHOOT*math.cos(visArea_center_rad)
        y_target = y_ball + BALL_DISTANCE_FOR_SHOOT*math.sin(visArea_center_rad)
    
        self.attacker.state.target_position = (Pose2D)(x_target, y_target, visArea_center_rad)

        return pt.common.Status.SUCCESS


class Align(pt.behaviour.Behaviour):
    def __init__(
        self,
        attacker: Bob,
        name: str = "Align_for_shoot",
        tolerance_rad=0.15,
        tolerance_xy=30,
    ):
        super().__init__(name)
        self.attacker = attacker
        self.bb = Blackboard_Manager.get_instance()
        self.tolerance_rad = tolerance_rad
        self.tolerance_xy = tolerance_xy

    def setup(self, **kwargs):
        if self.attacker is None:
            raise RuntimeError(f"[{self.name}] Robôs não definidos no setup()")
        return super().setup(**kwargs)

    def initialise(self):
        self.bb.set(f"{self.attacker.robot_id.name}_cmd_movement", 0.0)

    def update(self) -> pt.common.Status:

      if (
          self.attacker is None
          or self.attacker.state is None
      ):
          return pt.common.Status.FAILURE
    
      # Realiza o movimento
      self.attacker.precision_movement()

      attacker_id = self.attacker.robot_id.value   # Transforma de enum para int
      attacker_pose = _ws.get_team_robot_pose(attacker_id)


      if hp.PositioningHelper.is_aligned_to_goal(
            attacker_pose,
            self.attacker.state.target_position,
            tolerance_rad = self.tolerance_rad,
            tolerance_xy = self.tolerance_xy
        ):
          print("sucess")
          return pt.common.Status.SUCCESS
      else:
          print("running")
          return pt.common.Status.RUNNING


    def terminate(self, new_status: pt.common.Status):
      self.bb.set(f"{self.attacker.robot_id.name}_cmd_movement", 0.0)
      


### NAO SEI EXATAMENTE EM Q PONTO ISSO É CHAMADO, MAS ELE PRECISA ESTAR COLADO NA BOLA
### EU SEI Q NÃO TEM COMO GARANTIR ISSO, MAS O COMANDO PARA ISSO SER FEITO DEVE TER SIDO
### EXECUTADO ANTES DE CHEGAR AQUI
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

    def update(self) -> pt.common.Status:
        if self.attacker is None or self.attacker.state is None:
            return pt.common.Status.FAILURE

        kick_cmd = self.attacker.kick_ball()

        if not kick_cmd:
            return pt.common.Status.FAILURE
        else:
            return pt.common.Status.SUCCESS

    def terminate(self, new_status: pt.common.Status):
        self.bb.set(f"{self.attacker.robot_id.name}_team_kick", False)
