# core/bob_manager.py
from __future__ import annotations

import math
from typing import Dict, List, Optional

from SSL_configuration.configuration import Configuration
from utils import defines
from utils.pose2D import Pose2D

from ..core.event_callbacks import Event, EventManager
from ..core.World_State import World_State
from .bob import Bob, TeamID
from .FoeState import FoesID, FoeState
from .Manager import Manager


class BobManager(Manager):
    _instance: BobManager | None = None

    def __init__(self):
        self.eventManager = EventManager.get_instance()
        self.bobs: Dict[TeamID, Bob] = {}
        self.foes: Dict[FoesID, FoeState] = {}
        self.configuration = Configuration.getObject()
        self.world_state = World_State.get_object()
        self.ball_position: Optional[Pose2D] = None
        self.teamHasBall = 0
        self.foesHaveBall = 0

    @staticmethod
    def get_instance() -> BobManager:
        if BobManager._instance is None:
            BobManager._instance = BobManager()
            BobManager._instance.initialize()
        return BobManager._instance

    def initialize(self):
        """Cria as instâncias de Bob."""
        self.bobs[TeamID.Kamiji] = Bob(TeamID.Kamiji)
        self.bobs[TeamID.Argenton] = Bob(TeamID.Argenton)
        self.bobs[TeamID.SabKawa] = Bob(TeamID.SabKawa)
        self.foes[FoesID.Cerberus] = FoeState(FoesID.Cerberus)
        self.foes[FoesID.TauraBots] = FoeState(FoesID.TauraBots)
        self.foes[FoesID.GralhaBots] = FoeState(FoesID.GralhaBots)
        self.eventManager.emit(Event.FOES_GOT_BALL_POSSESSION)
        self.eventManager.emit(Event.TEAM_GOT_BALL_POSSESSION)

    def update(self):
        """Atualiza o estado global de todos os robôs."""
        self.ball_position = self.world_state.get_ball_position()
        self.teamUpdate()
        self.teamGotBall()
        self.teamReachedTarget()
        self.teamReachedAngle()
        self.foesUpdate()
        self.foesGotBall()

    def teamUpdate(self):
        """Atualiza as posições dos robôs do time."""
        for teamID in TeamID:
            bob = self.bobs.get(teamID)
            if not bob:
                continue
            pose = self.world_state.get_team_robot_pose(teamID.value)
            self.eventManager.emit(Event.TARGET_RESET, teamID.name)
            if pose is not None:
                bob.state.position = pose

    def foesUpdate(self):
        """Atualiza as posições dos robôs inimigos."""
        for robot_id in FoesID:
            foe = self.foes.get(robot_id)
            if not foe:
                continue
            pose = self.world_state.get_foe_robot_pose(robot_id.value)
            if pose is not None:
                foe.position = pose

    def foesGotBall(self):
        """Verifica e atualiza posse de bola."""
        for foeID in FoesID:
            foe = self.foes.get(foeID)
            if not foe:
                continue
            has_possession_now = self.checkBallPossession(foe.position, foe.has_ball)
            changed = foe.has_ball != has_possession_now

            if changed:
                if has_possession_now:
                    # evento: "ganhou_posse"
                    self.foesHaveBall += 1
                    self.eventManager.emit(Event.FOES_GOT_BALL_POSSESSION)
                    self.eventManager.emit(Event.GOT_BALL_POSSESSION, foeID)

                else:
                    # evento: "perdeu_posse"
                    self.eventManager.emit(Event.LOST_BALL_POSSESSION, foeID.name)
                    self.foesHaveBall -= 1
                    if self.foesHaveBall <= 0:
                        self.eventManager.emit(Event.FOES_LOST_BALL_POSSESSION)
                        self.foesHaveBall = 0

            foe.has_ball = has_possession_now

    def teamGotBall(self):
        """Verifica e atualiza posse de bola."""
        for teamID in TeamID:
            bob = self.bobs.get(teamID)
            if not bob:
                continue
            robot = bob.state
            has_possession_now = self.checkBallPossession(
                robot.position, robot.has_ball
            )
            changed = robot.has_ball != has_possession_now
            if changed:
                if has_possession_now:
                    # evento: "ganhou_posse"
                    self.teamHasBall += 1
                    self.eventManager.emit(Event.TEAM_GOT_BALL_POSSESSION)
                    self.eventManager.emit(Event.GOT_BALL_POSSESSION, teamID.name)
                else:
                    # evento: "perdeu_posse"
                    self.eventManager.emit(Event.LOST_BALL_POSSESSION, teamID.name)
                    self.teamHasBall -= 1
                    if self.teamHasBall <= 0:
                        self.eventManager.emit(Event.TEAM_LOST_BALL_POSSESSION)
                        self.teamHasBall = 0

            robot.has_ball = has_possession_now

    def checkBallPossession(
        self, position: Optional[Pose2D], has_possession_now: bool
    ) -> bool:
        ball_position = self.ball_position or self.world_state.get_ball_position()

        if position is None or ball_position is None:
            return False

        dist = position.distance_to(ball_position)

        if has_possession_now:
            return dist <= defines.BALL_LOSS_DISTANCE
        else:
            return dist <= defines.BALL_POSSESSION_DISTANCE

    def teamReachedTarget(self):
        """Gerencia o progresso dos robôs em seus caminhos (path)."""
        thresh = 20

        for teamID in TeamID:
            if not (bob := self.bobs.get(teamID)):
                return

            if not bob.state.path or bob.state.target_theta:
                return

            bob.state.target_position = bob.state.path[bob.state._path_index]
            if bob.state.target_position.is_in_range(
                bob.state.position, self.configuration.threshould_arrived_target
            ):
                if bob.state._path_index >= len(bob.state.path) - 1:
                    bob.state.path.clear()
                    bob.state._path_index = 0
                    self.eventManager.emit(Event.TARGET_REACHED, teamID.name)
                else:
                    bob.state._path_index += 1

    def teamReachedAngle(self):
        """Verifica se o robô alcançou o ângulo desejado."""
        tol = getattr(self.configuration, "threshold_arrived_theta", 0.1)

        for teamID in TeamID:
            bob = self.bobs.get(teamID)
            if not bob:
                continue
            robot = bob.state

            if robot.target_theta is not None and robot.position is not None:
                if self._angle_diff(robot.target_theta, robot.position.theta) <= tol:
                    robot.target_theta = None
                    # TODO: evento "chegou_theta"

    @staticmethod
    def _angle_diff(a: float, b: float) -> float:
        """Diferença mínima entre ângulos a e b (resultado em [0, π])."""
        d = (a - b) % (2 * math.pi)
        if d > math.pi:
            d -= 2 * math.pi
        return abs(d)
