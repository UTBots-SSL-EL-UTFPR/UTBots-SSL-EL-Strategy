# core/bob_manager.py
from __future__ import annotations

import math
from typing import Dict

from Behaviour_tree.helpers.field_helper import FIELD_X_MAX, FIELD_X_MIN, HALF_LEGHT
from Behaviour_tree.helpers.motion_helper import MotionHelper
from Behaviour_tree.helpers.positioning_helper import PositioningHelper
from Behaviour_tree.trees.tree import Tree
from SSL_configuration.configuration import Configuration
from utils.defines import FIELD_INVERTED_SIDE  # BOB_RADIUS,
from utils.defines import BALL_RADIUS, MIN_PASS_DISTANCE, ROBOT_RADIUS
from utils.pose2D import Pose2D, QuadrantType, RoleType, ZoneType

from .core.World_State import FoesID, TeamID, World_State
from .robot.bob import Bob


class BobManager:
    _instance = None
    """
    Responsável por instanciar e gerenciar todos os robôs e suas árvores de comportamento.
    """

    def __init__(self):
        self.bobs: Dict[TeamID, Bob] = {}

        self.trees: Dict[TeamID, Tree] = {}
        self.configuration = Configuration.getObject()
        self.world_state = World_State.get_object()
        self.positioning_helper = PositioningHelper.get_object()

        self._create_bob(TeamID.Kamiji)
        self._create_bob(TeamID.Argenton)
        self._create_bob(TeamID.SabKawa)

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
            robot_id (TeamID): ID do robô.
            tree (Tree): Classe da árvore associada.
        """
        bob = Bob(robot_id=robot_id)
        # bob.state.reset()
        self.bobs[robot_id] = bob
        # self.trees[robot_id] = tree(bob)

    def update_all(self):
        self.ball_pos = self.world_state.get_ball_position()

        for bob in self.bobs.values():
            if bob.state:
                bob.state.update()

    def tick_all(self):
        for tree in self.trees.values():
            tree.tick()

    def get_bob(self, robot_id):
        return self.bobs.get(robot_id)

    def get_tree(self, robot_id):
        return self.trees.get(robot_id)

    # ---------------------------------------#
    #        Último homem (global)          #
    # ---------------------------------------#
    def get_last_man(self):
        """
        Retorna informações do robô (aliado ou oponente) que está MAIS PRÓXIMO do nosso gol
        ao longo do eixo X, considerando o lado em que defendemos.

        - Se defendemos a ESQUERDA (FIELD_INVERTED_SIDE == False): procura o menor X.
        - Se defendemos a DIREITA (FIELD_INVERTED_SIDE == True): procura o maior X.

        Retorno:
            dict com chaves:
                team: 'ally' | 'foe'
                id: TeamID | None           (preenchido se ally)
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

    def get_last_man_id(self) -> TeamID | None:
        """
        Retorna o TeamID do "último homem" se ele for do nosso time; caso o último seja oponente,
        retorna None. Use get_last_man() para detalhes quando for oponente.
        """
        info = self.get_last_man()
        if info and info["team"] == "ally":
            return info["id"]
        return None

    # def set_bob_freekick_position(self):
    #     """
    #     Decide metas de posicionamento para **goleiro**, **cobrador** e **apoio** em bola parada ofensiva.
    #     Para bola parada defenciva, podemos ter goleiro cobrador e  2 apoio
    #     """
    #     if self.ball_pos.x < self.configuration.max_ball_y_to_goalkeeper_kick: # type: ignore
    #         self.set_offensive_suport_position(TeamID.Kamiji)
    #         aux = self.bobs.get(TeamID.Kamiji)
    #         if not aux or not aux.state:
    #             return
    #         pos = aux.state.path[len(aux.state.path) - 1]
    #         self.set_midlle_suport_position(TeamID.Defender, pos) # type: ignore
    #         self.set_kicker_position(TeamID.Goalkeeper)
    #     else:
    #         self.set_kicker_position(TeamID.Kamiji)

    #         self.set_offensive_suport_position(TeamID.Defender)
    #         print("tres")

    #         self.set_goalkeeper_position(TeamID.Goalkeeper)
    #         print("quatro")

    #     return


if __name__ == "__main__":
    pass
