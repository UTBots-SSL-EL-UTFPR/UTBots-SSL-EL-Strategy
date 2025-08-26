# core/bob_manager.py
from __future__ import annotations
from Behaviour_tree.trees.tree import Tree
from .robot.bob import Bob

from typing import Dict
from utils.pose2D import Pose2D
from utils.defines import RoleType, ZoneType
from .core.World_State import World_State
from .core.World_State import RobotID
from SSL_configuration.configuration import Configuration
import math
from .positioning.positioning_helper import Positioning_helper

class BobManager:
    _instance = None
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.bobs: Dict[RobotID, Bob] = {}
        
        self.trees: Dict[RobotID, Tree] = {}

        self.world_state = World_State.get_object()
        self.positioning_helper = Positioning_helper.get_object()

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

        target = Pose2D.align_two(self.ball_pos, Pose2D(2500, 0), 200, True) #TODO fazer gol dinamico (troca de lados)
        obstacles = self.world_state.get_all_robot_position()
        for obs in obstacles:
            if obs == robot.state.position:
                obstacles.remove(obs)
        robot.state.path = robot.find_shortest_path(robot.state.position, target, obstacles, 80, self.ball_pos, 15)

        
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    def set_offensive_suport_position(self, id: RobotID):
        """
        Calcula e define a posição do robô de SUPORTE OFENSIVO com base em:
        1) Lado de preferência do adversário (mais robôs com y > 0 ⇒ preferem "alto");
        2) Restrição do espaço ao QUADRANTE AVANÇADO (metade ofensiva) do LADO MAIS LIVRE;
        3) Limitações: margens de campo, fora da área do goleiro e fora do raio de influência dos inimigos;
        4) Seleção: ponto VÁLIDO mais próximo do centro do gol adversário (empate ⇒ ponto mais seguro).

        Grava em robot.state.target_position e define o papel OFFENSIVE_SUPPORT.
        Retorna a Pose2D alvo.
        """
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return None
        
        free_quadrants = self.positioning_helper.get_atack_quadrant_free(100)

        obstacles = self.world_state.get_all_robot_position()
        for obs in obstacles:
            if obs == robot.state.position:
                obstacles.remove(obs)
        target_pose = Pose2D() #TODO
        robot.state.path = robot.find_shortest_path(robot.state.position, target_pose, obstacles, 80, self.ball_pos, 15)
        robot.state.role = RoleType.OFFENSIVE_SUPPORT




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
