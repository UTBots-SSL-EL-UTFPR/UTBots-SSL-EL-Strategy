"""
Todos os comportamentos de ação, classes instanciadas com biblioteca pytree
"""
from __future__ import annotations
from time import sleep
from ...core.World_State import World_State, RobotID
import py_trees
from ...core.event_callbacks import BB_flags_and_values

from Behaviour_tree.core.blackboard import Blackboard_Manager
import time
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from  Behaviour_tree.core import event_callbacks as callbacks
navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions
team_flags = BB_flags_and_values.Flags.Team_Flags


from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.positioning.positioning_helper import Positioning_helper
#---------------------------------------------------------------------------------------#
#                                         MOVIMENTO                                     #
#---------------------------------------------------------------------------------------#

from typing import Optional, Tuple
import time
import py_trees as pt

class Move_node(pt.behaviour.Behaviour):
    """
    Nó de movimento genérico: empurra o robô  até robot.state.target_position (path inteiro)

    :param name: Nome do nó.
    :type name: str
    :param robot: Instância do robô (Bob).
    :type robot: Bob | None
    :param target_reached_key: Chave do Blackboard que sinaliza 'alvo alcançado' (bool).
                               Ex.: f\"{robot.robot_id.name}{navigation_flags.target_reached}\".
    :type target_reached_key: str
    :param timeout_s: Tempo máximo (segundos) para tentar alcançar o alvo antes de retornar FAILURE.
    :type timeout_s: float
    """

    def __init__(
        self,
        name: str = "MOVE",
        robot = None,
        timeout_s: float = 3.0,
    ):
        super().__init__(name=name)
        self.robot :  Bob | None = robot
        self._bb = Blackboard_Manager.get_instance()

        self.target_reached_key = ""
        self.timeout_s = timeout_s

        self._t0: float = 0.0
        self._last_move_ts: float = 0.0
        self._stall_ticks: int = 0
        self._max_stall_ticks: int = 30 


    def setup(self, **kwargs) -> None:
        """
        Prepara o nó para execução. Registre chaves do BB aqui se sua API suportar.

        :raises RuntimeError: se 'robot' não estiver definido.
        """
        print("setup")
        if self.robot is None:
            raise RuntimeError(f"[{self.name}] 'robot' não definido no setup()")
        self.target_reached_key = f"{self.robot.robot_id.name}{navigation_flags.target_reached}"

    def initialise(self) -> None:
        """
        Chamado no primeiro tick ativo (ou reentrada). Zera temporais, limpa flags,
        e carrega alvo do BB para o estado do robô se necessário.
        """
        if self.robot is None or self.robot.state is None:
            return
        self._t0 = time.time()
        self._last_move_ts = self._t0
        self._stall_ticks = 0
        self._bb.set(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}", False) # type: ignore
        print(f"{self.robot.robot_id} -> INIT MOVEMENT")

        self._bb.set(self.target_reached_key, False)

    def update(self) -> pt.common.Status:
        """
        Empurra o robô a mover-se (via `robot.move_oriented()`) enquanto não atingiu o alvo.
        Depende do Blackboard para saber se o alvo foi alcançado (`target_reached_key`).

        :returns: SUCCESS quando alvo alcançado; RUNNING durante o deslocamento; FAILURE em erro/timeout.
        :rtype: pt.common.Status
        """
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE

        if bool(self._bb.get(self.target_reached_key)):
            print(f"{self.robot.robot_id} -> TARGET REACHED")
            return pt.common.Status.SUCCESS

        if not getattr(self.robot.state, "target_position", None):
            return pt.common.Status.FAILURE

        try:
            self.robot.move_oriented() 
        except Exception as exc:
            return pt.common.Status.FAILURE

        if (time.time() - self._t0) > self.timeout_s:
            print(f"{self.robot.robot_id} -> MOVE TIMEOUT")
            return pt.common.Status.FAILURE

        if self._bb.get(f"{self.robot.robot_id.name}{navigation_flags.is_stuck}"):
            print(f"{self.robot.robot_id} -> ROBOT STUCK")
            return pt.common.Status.FAILURE
        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status) -> None:
        """
        Limpa estado local e o alvo do robô. Dispara callback de reset.

        :param new_status: status no qual o nó terminou (SUCCESS/FAILURE/INVALID).
        :type new_status: pt.common.Status
        """
        if self.robot is None or getattr(self.robot, "state", None) is None:
            return

        self.robot.state.target_position = None

        try:
            callbacks.target_reset(self.robot.robot_id.name)
        except Exception:
            pass


#---------------------------------------------------------------------------------------#
#                                      PASSE                                            A#
#---------------------------------------------------------------------------------------# 

class Choose_who_to_pass(py_trees.behaviour.Behaviour):

    def __init__(self, Robot:Bob, name):
        super().__init__(name)
        self.robot = Robot
        self.target: tuple[float, float]
        self.bb = Blackboard_Manager.get_instance()
        self.position = self.bb.get(f"{Robot.robot_id}{positions.quadrant}")

    def setup(self,**kwargs):
        return super().setup(**kwargs)
    
    def update(self):
       
        if self.robot is None or self.robot.state is None:
            return py_trees.common.Status.FAILURE   
        if self.position is None:
            return py_trees.common.Status.FAILURE
        
        if self.position % 4 == 0:#######Esta no ultimo quarto do campo , irá chutar no gol
            return py_trees.common.Status.FAILURE
            
        
        best_target_pos =None
        best_target_id  =None
        if self.robot.robot_id == 2:
          
            target0 =RobotID(0)
            target1 = RobotID(1)

            #Passar para o jogador mais proximo
            
            min_distance = 1000000

            for robot_id in [target0,target1]:
                pos = self.bb.get(f"{robot_id}{positions.position}")
                if pos is not None:
                    distance = ((self.robot.state.position.x - pos[0])**2 + (self.robot.state.position.y - pos[1])**2)**0.5
                    if distance < min_distance:
                        min_distance = distance
                        best_target_pos = pos
                        best_target_id = robot_id

                    if best_target_pos is not None:
                        self.target = best_target_pos
                        self.bb.on_pass(self.robot.robot_id.name)
                        
                    
        elif self.robot.robot_id == 1:
            best_target_id = RobotID(0)
            best_target_pos = self.bb.get(f"{best_target_id}{positions.position}")
            if best_target_pos is not None:
                self.target = best_target_pos
                self.bb.on_pass(self.robot.robot_id.name)
                
            
        else:
            best_target_id = RobotID(1)
            best_target_pos = self.bb.get(f"{best_target_id}{positions.position}")
            if best_target_pos is not None:
                self.target = best_target_pos
                self.bb.on_pass(self.robot.robot_id.name)
        

        if self.bb.get(f"{team_flags.Context.is_pass}"):
            return py_trees.common.Status.SUCCESS
        else:
            return py_trees.common.Status.FAILURE


            
            #self.target = (1000,0)
            #self.bb.set(f"{self.robot.robot_id.name}{positions.target_to_pass}",self.target)
            #return py_trees.common.Status.SUCCESS    
 
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
        tolerance: float = 0.15
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
            self.passer is None or self.receiver is None or
            self.passer.state is None or self.receiver.state is None
        ):
            return pt.common.Status.FAILURE

        passer_pose = self.passer.state.position
        receiver_pose = self.receiver.state.position
        goal_pose = self.bb.get("goal_pose")

        # Verificação sem considerar oponentes
        if Positioning_helper.are_pass_orientations_aligned(
            passer_pose, receiver_pose, goal_pose, opponents=[], tolerance=self.tolerance
        ):
            return pt.common.Status.SUCCESS

        # Ângulo ideal receptor
        desired_receiver_angle = Positioning_helper.get_best_pass_orientation(
            passer_pose, receiver_pose, goal_pose, opponents=[]
        )
        # Ângulo ideal passador (olhando pro receptor)
        desired_passer_angle = math.atan2(
            receiver_pose.y - passer_pose.y,
            receiver_pose.x - passer_pose.x
        )

        # Ajustar passador
        angle_diff_passer = (desired_passer_angle - passer_pose.theta + math.pi) % (2*math.pi) - math.pi
        if abs(angle_diff_passer) > self.tolerance:
            self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", angle_diff_passer)

        # Ajustar receptor
        angle_diff_receiver = (desired_receiver_angle - receiver_pose.theta + math.pi) % (2*math.pi) - math.pi
        if abs(angle_diff_receiver) > self.tolerance:
            self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", angle_diff_receiver)

        return pt.common.Status.RUNNING

    def terminate(self, new_status: pt.common.Status):
        self.bb.set(f"{self.passer.robot_id.name}_cmd_rotation", 0.0)
        self.bb.set(f"{self.receiver.robot_id.name}_cmd_rotation", 0.0)
      