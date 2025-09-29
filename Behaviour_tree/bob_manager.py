# core/bob_manager.py
from __future__ import annotations

import math
from typing import Dict

from Behaviour_tree.helpers.field_helper import FIELD_X_MAX, FIELD_X_MIN, HALF_LEGHT
from Behaviour_tree.helpers.motion_helper import MotionHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.trees.tree import Tree
from SSL_configuration.configuration import Configuration
from utils.defines import BALL_RADIUS, FIELD_INVERTED_SIDE, ROBOT_RADIUS
from utils.pose2D import Pose2D, QuadrantType, RoleType

from .core.World_State import RobotID, World_State
from .robot.bob import Bob


class BobManager:
    _instance = None
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.bobs: Dict[RobotID, Bob] = {}
        
        self.trees: Dict[RobotID, Tree] = {}
        self.configuration = Configuration.getObject()
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
        #bob.state.reset()
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
        new_path = MotionHelper.find_shortest_path(
            robot.state.position,
            target,
            obstacles,
            self.ball_pos,
        )
        robot.set_path(new_path)

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    def set_midlle_suport_position(self, id: RobotID, main_suport_pose: Pose2D):
        """
        Posiciona o robô de "suporte do meio".

        A lógica é:
        1. Escolher o lado do campo (Y positivo ou negativo) oposto ao do suporte principal.
        2. Mirar em um ponto pré-definido nesse lado (X=1300, Y=+-1000).
        3. Verificar se há oponentes próximos a este ponto alvo.
        4. Se houver, ajustar a posição para ficar "à frente" do oponente
        """
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return None
        TARGET_X = 1300
        TARGET_Y_MAGNITUDE = 1000
        SAFE_OPPONENT_DISTANCE = 400


        if main_suport_pose.y >= 0:
            primary_target = Pose2D(TARGET_X, -TARGET_Y_MAGNITUDE)
        else:
            primary_target = Pose2D(TARGET_X, TARGET_Y_MAGNITUDE)

        opponents = self.world_state.get_all_foes_position()
        target_pose = primary_target 

        if opponents:
            closest_opponent = min(opponents, key=lambda opp: opp.distance_to(primary_target))
            dist_to_closest = primary_target.distance_to(closest_opponent)

            if dist_to_closest < SAFE_OPPONENT_DISTANCE:

                new_x = closest_opponent.x + SAFE_OPPONENT_DISTANCE
                
                if new_x > HALF_LEGHT - 200:
                    new_x = HALF_LEGHT - 200

                target_pose = Pose2D(new_x, primary_target.y)

        obstacles = self.world_state.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot.state.position]
        
        robot.state.target_position = target_pose
        new_path = MotionHelper.find_shortest_path(
            robot.state.position,
            target_pose,
            obstacles,
            self.ball_pos,
        )
        robot.set_path(new_path)
        robot.state.role = RoleType.DEFENSIVE_SUPPORT
        
        return target_pose


    def set_goalkeeper_position(self, id: RobotID):
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return None
        robot_pos = robot.state.position
        self.ball_pos
        obstacles = self.world_state.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot_pos]

        target_pose = Pose2D(-100, 0)
        new_path = MotionHelper.find_shortest_path(
            robot.state.position,
            target_pose,
            obstacles,
            self.ball_pos,
        )
        robot.set_path(new_path)
        robot.state.role = RoleType.OFFENSIVE_SUPPORT
    
    def set_goalkeeper_defense_position(self, id: RobotID):
        """Posiciona o goleiro para defender com base na posição atual da bola.

        Estratégia:
        - Projeta a posição da bola dentro da faixa vertical da área do goleiro.
        - Mantém o goleiro em uma "linha de corte" entre a bola e o centro do gol.
        - Restringe movimento ao retângulo da área de goleiro.
        - Usa path planning para gerar caminho até o alvo.
        """
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return None

        # Definição da área do goleiro (lado depende do FIELD_INVERTED_SIDE)
        if not FIELD_INVERTED_SIDE:
            # Defende gol da esquerda
            area_x_min, area_x_max = -2250, -1650
        else:
            # Espelho para gol da direita
            area_x_min, area_x_max = 1650, 2250
        area_y_min, area_y_max = -600, 600

        ball = self.ball_pos if self.ball_pos else self.world_state.get_ball_position()
        if ball is None:
            return None

        # Centro do gol defendido
        goal_x = FIELD_X_MIN if not FIELD_INVERTED_SIDE else FIELD_X_MAX
        goal_center_y = 0.0

        # Projeta y da bola dentro da área
        target_y = max(area_y_min + 50, min(ball.y, area_y_max - 50))

        # Distância horizontal relativa bola -> gol
        dist_ball_to_goal = abs(ball.x - goal_x)
        # Profundidade base: mais à frente se a bola está longe, mais recuado se está perto
        if dist_ball_to_goal < 300:
            depth_factor = 0.1  # cola mais na linha
        elif dist_ball_to_goal < 800:
            depth_factor = 0.35
        else:
            depth_factor = 0.6

        # Calcula x alvo dentro da área: interpolação entre linha do gol e borda externa da área
        if not FIELD_INVERTED_SIDE:
            # Área à esquerda (x crescente para fora)
            target_x = goal_x + (area_x_max - goal_x) * depth_factor
        else:
            # Área à direita (x decrescente para fora)
            target_x = goal_x + (area_x_min - goal_x) * depth_factor

        # Clamp final dentro da área
        target_x = int(max(area_x_min + 20, min(target_x, area_x_max - 20)))

        target_pose = Pose2D(target_x, target_y)

        # Planejamento de caminho
        obstacles = self.world_state.get_all_robot_position()
        obstacles = [obs for obs in obstacles if obs != robot.state.position]
        robot.state.target_position = target_pose
        new_path = MotionHelper.find_shortest_path(
            robot.state.position,
            target_pose,
            obstacles,
            self.ball_pos,
        )
        robot.set_path(new_path)
        robot.state.role = RoleType.GOALKEEPER
        return target_pose

    #---------------------------------------#
    #        Último homem (global)          #
    #---------------------------------------#
    def get_last_man(self):
        """
        Retorna informações do robô (aliado ou oponente) que está MAIS PRÓXIMO do nosso gol
        ao longo do eixo X, considerando o lado em que defendemos.

        - Se defendemos a ESQUERDA (FIELD_INVERTED_SIDE == False): procura o menor X.
        - Se defendemos a DIREITA (FIELD_INVERTED_SIDE == True): procura o maior X.

        Retorno:
            dict com chaves:
                team: 'ally' | 'foe'
                id: RobotID | None           (preenchido se ally)
                index: int | None            (índice na lista de foes, se foe)
                pos: Pose2D                  (posição do robô)
        """
        goal_is_right = FIELD_INVERTED_SIDE

        # Aliados (com ID)
        ally_candidates = []
        for rid, bob in self.bobs.items():
            if bob and bob.state:
                ally_candidates.append((rid, bob.state.position))

        # Oponentes (sem ID explícito disponível aqui, usamos índice)
        foe_positions = self.world_state.get_all_foes_position()
        foe_candidates = list(enumerate(foe_positions)) if foe_positions else []

        # Função de chave conforme o lado defendido
        key_fn = (lambda p: p.x) if goal_is_right else (lambda p: -p.x)
        # Usamos -x para lado esquerdo, de forma que min() funcione com a mesma lógica a seguir

        best_item = None
        best_key = None

        # Varre aliados
        for rid, pos in ally_candidates:
            k = key_fn(pos)
            if best_key is None or k < best_key:
                best_key = k
                best_item = {"team": "ally", "id": rid, "index": None, "pos": pos}

        # Varre oponentes
        for idx, pos in foe_candidates:
            k = key_fn(pos)
            if best_key is None or k < best_key:
                best_key = k
                best_item = {"team": "foe", "id": None, "index": idx, "pos": pos}

        return best_item

    def get_last_man_id(self) -> RobotID | None:
        """
        Retorna o RobotID do "último homem" se ele for do nosso time; caso o último seja oponente,
        retorna None. Use get_last_man() para detalhes quando for oponente.
        """
        info = self.get_last_man()
        if info and info["team"] == "ally":
            return info["id"]
        return None
    

    def set_bob_freekick_position(self):
        """
        Decide metas de posicionamento para **goleiro**, **cobrador** e **apoio** em bola parada ofensiva.
        Para bola parada defenciva, podemos ter goleiro cobrador e  2 apoio
        """
        if self.ball_pos.x < self.configuration.max_ball_y_to_goalkeeper_kick: # type: ignore
            self.set_offensive_suport_position(RobotID.Kamiji)
            aux = self.bobs.get(RobotID.Kamiji)
            if not aux or not aux.state:
                return
            pos = aux.state.path[len(aux.state.path) - 1]
            self.set_midlle_suport_position(RobotID.Defender, pos) # type: ignore
            self.set_kicker_position(RobotID.Goalkeeper)
        else:
            self.set_kicker_position(RobotID.Kamiji)

            self.set_offensive_suport_position(RobotID.Defender)
            print("tres")

            self.set_goalkeeper_position(RobotID.Goalkeeper)
            print("quatro")

        return 


if __name__ == "__main__":
    pass
