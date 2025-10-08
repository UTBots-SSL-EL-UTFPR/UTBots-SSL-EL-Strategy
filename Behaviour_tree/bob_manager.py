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

from .core.World_State import TeamID, World_State
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
            robot_id (RobotID): ID do robô.
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
    #               Posicionamento          #
    # ---------------------------------------#

    def set_kicker_position(self, id: TeamID):
        robot = self.bobs.get(id)
        if robot is None or robot.state is None:
            return
        robot.state.role = RoleType.KICKER

        target = Pose2D.align_two(
            self.ball_pos, Pose2D(2500, 0), 200, True
        )  # TODO fazer gol dinamico (troca de lados)
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

    def set_midlle_suport_position(self, id: TeamID, main_suport_pose: Pose2D):
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
            closest_opponent = min(
                opponents, key=lambda opp: opp.distance_to(primary_target)
            )
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


if __name__ == "__main__":
    pass
