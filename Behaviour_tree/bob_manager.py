# core/bob_manager.py

from Behaviour_tree.trees.tree import Tree
from .robot.bob import Bob
from .trees.bob_trees.kamiji_tree import KamijiTree
from .trees.bob_trees.defender_tree import Defender_tree
from .trees.bob_trees.goalkeeper_tree import Goalkeeper_tree
from .core.World_State import RobotID
from typing import Dict
from utils.pose2D import Pose2D
from utils.defines import RoleType, Zone_Type
from .core.World_State import World_State
from SSL_configuration.configuration import Configuration
import math

class BobManager:
    _instance = None
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.bobs: Dict[RobotID, Bob] = {}
        
        self.trees: Dict[RobotID, Tree] = {}

        self.world_state = World_State.get_object()
        self.configuration = Configuration.getObject()

        self._create_bob(RobotID.Kamiji)
        self._create_bob(RobotID.Defender)
        self._create_bob(RobotID.Goalkeeper)

        self.ball_pos = Pose2D()

    @staticmethod
    def get_object():
        if not BobManager._instance:
            BobManager._instance = BobManager()
        return BobManager._instance
    
    def _create_bob(self, robot_id):
        """
        Cria uma instância de Bob e associa à sua árvore.

        Args:
            robot_id (RobotID): ID do robô.
            tree (Tree): Classe da árvore associada.
        """
        bob = Bob(robot_id=robot_id)
        bob.state.reset()
        self.bobs[robot_id] = bob
        #self.trees[robot_id] = tree(bob)

    def update_all(self):
        self.ball_pos = self.world_state.get_ball_position()

        for bob in self.bobs.values():
            if(bob.state):
                bob.state.update()

    def tick_all(self):
        for tree in self.trees.values():
            tree.tick()

    def get_bob(self, robot_id):
        return self.bobs.get(robot_id)

    def get_tree(self, robot_id):
        return self.trees.get(robot_id)
    
    #---------------------------------------#
    #               Posicionamento          #
    #---------------------------------------#

    def set_kicker_position(self, id: RobotID):
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return
        robot.state.role = RoleType.KICKER
        print(f"ball: {self.ball_pos}")

        target = Pose2D.align_two(self.ball_pos, Pose2D(2500, 0), 200, True) #TODO fazer gol dinamico (troca de lados)
        print(f"target: {target}")
        obstacles = self.world_state.get_all_robot_position()
        for obs in obstacles:
            if obs == robot.state.position:
                obstacles.remove(obs)
        robot.state.path = robot.find_shortest_path(robot.state.position, target, obstacles, 15, self.ball_pos,15)
        #robot.adicionar_ponto_trajetoria(target)



    def set_offensive_suport_position(self, id: RobotID):
        """
        Define uma posição ofensiva de suporte para o robô especificado.

        Estratégia:
        - Calcula um ponto lateral à linha bola→gol, a uma distância fixa.
        - Corrige a posição para garantir que fique dentro do campo e fora da área do goleiro.

        :param id: Identificador do robô (RobotID).
        """

        bx, by = self.ball_pos 
        goal_x, goal_y = self.configuration.goal_position_x, 0
        dist_from_ball = self.configuration.suport_dist_from_ball if self.configuration.suport_dist_from_ball is not None else 0
        prefer_left = True

        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return
        robot.state.role = RoleType.OFFENSIVE_SUPPORT

        # ------------------------
        # 2) Calcula candidato de apoio (_support_candidate)
        # ------------------------

        theta = math.atan2(goal_y - by, goal_x - bx) # type: ignore
        nx, ny = -math.sin(theta), math.cos(theta)
        if not prefer_left:
            nx, ny = -nx, -ny

        cx = bx + nx * dist_from_ball
        cy = by + ny * dist_from_ball

        # ------------------------
        # 3) Corrige para dentro do campo (_push_safe)
        # ------------------------
        half_len = 4500 / 2.0
        half_wid = 3000 / 2.0
        margin = 300.0  # margem de segurança

        # clamp nos limites
        cx = max(-half_len + margin, min(half_len - margin, cx))
        cy = max(-half_wid + margin, min(half_wid - margin, cy))

        # se caiu dentro da área do goleiro, empurra para fora
        if robot.state.position.get_zone() != Zone_Type.FOE_GOALKEEPER_ZONE:
            if self.side > 0:
                cx = -half_len + self.field.keeper_area_length + margin
            else:
                cx = half_len - self.field.keeper_area_length - margin

        # ------------------------
        # 4) Define orientação e salva
        # ------------------------
        theta_face_ball = math.atan2(by - cy, bx - cx)
        target_pose = Pose2D(cx, cy, theta_face_ball)

        # salva no robô ou no blackboard
        self.robots[id].target_pose = target_pose
        return target_pose

        
    def set_midlle_suport_position(self, id: RobotID):
        pass
    def set_goalkeeper_position(self, id: RobotID):
        pass
    

    def set_bob_freekick_position(self):
        """
        Decide metas de posicionamento para **goleiro**, **cobrador** e **apoio** em bola parada ofensiva.
        Para bola parada defenciva, podemos ter goleiro cobrador e  2 apoio
        """
        if ball_pos.y < self.configuration.max_ball_y_to_goalkeeper_kick: # type: ignore
            self.set_offensive_suport_position(RobotID.Kamiji)
            self.set_midlle_suport_position(RobotID.Defender)
            self.set_kicker_position(RobotID.Goalkeeper)
        else:
            self.set_kicker_position(RobotID.Kamiji)
            self.set_offensive_suport_position(RobotID.Defender)
            self.set_goalkeeper_position(RobotID.Goalkeeper)
        return 


if __name__ == "__main__":
    p1 = Pose2D(0, 0)
    p3 = Pose2D(1000, 1500)

    print("---- Teste 3: Diagonal ----")

    pt_diag = Pose2D.align_two(p1, p3, margin=200, is_left_team=True)
    print("Obtido:  ", pt_diag, "\n")
