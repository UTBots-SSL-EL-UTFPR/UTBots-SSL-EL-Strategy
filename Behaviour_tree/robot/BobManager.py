# core/bob_manager.py
from __future__ import annotations

import math
from typing import Dict, List, Optional

from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.helpers.field_helper import FieldHelper
from SSL_configuration.configuration import Configuration
from utils import defines
from utils.pose2D import Pose2D

from ..core.event_callbacks import Event, EventManager
from ..core.World_State import World_State
from .bob import Bob, TeamID
from .FoeState import FoesID, FoeState
from .Manager import Manager

from ..observer_agents.EventNotifier import EventNotifier
from ..observer_agents.StateMachine import EventClass
from ..observer_agents.StateMachine import EventEnum


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
        self._bb = Blackboard_Manager.get_instance()
        self.evNotifier = EventNotifier.get_instance()

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
        for bob in TeamID:
            self.eventManager.emit(Event.BOB_LOST_BALL_POSSESSION, bob.name)
        for foe in FoesID:
            self.eventManager.emit(Event.FOE_LOST_BALL_POSSESSION, foe.name)

    def update(self):
        """Atualiza o estado global de todos os robôs."""
        self.ball_position = self.world_state.get_ball_position()
        if FieldHelper.get_team_goal_center().x * self.ball_position.x > 0:  
            self.evNotifier.reciveEvent(EventClass(EventEnum.PASSA_MEIO, True))
        else:
            self.evNotifier.reciveEvent(EventClass(EventEnum.PASSA_MEIO, False))

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
            ball_position = self.ball_position or self.world_state.get_ball_position()
            has_possession_now = (
                foe.position.distance_to(ball_position) <= defines.BALL_LOSS_DISTANCE
            )
            (f" quem ta co a bola agt ->{self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA)}")
            if (
                has_possession_now
                and self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA) is None
            ):
                if has_possession_now:
                    self.eventManager.emit(
                        Event.FOE_GOT_BALL_POSSESSION, foe.robot_id.name
                    )
                    self.evNotifier.reciveEvent(EventClass(EventEnum.FOES_HAS_BALL, True))

            elif (
                not has_possession_now
                and self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA) == foe.robot_id.name
            ):
                (foe.robot_id.name)
                self.eventManager.emit(Event.FOE_LOST_BALL_POSSESSION)
                self.evNotifier.reciveEvent(EventClass(EventEnum.FOES_HAS_BALL, False))

    def teamGotBall(self):
        """Verifica e atualiza posse de bola."""
        for teamID in TeamID:
            bob = self.bobs.get(teamID)
            if not bob:
                continue
            ball_position = self.ball_position or self.world_state.get_ball_position()
            has_possession_now = (
                bob.state.position.distance_to(ball_position)
                <= defines.BALL_LOSS_DISTANCE
            )
            (f" quem ta co a bola agt ->{self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA)}")
            if (
                has_possession_now
                and self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA) is None
            ):
                self.eventManager.emit(Event.BOB_GOT_BALL_POSSESSION, bob.robot_id.name)
                self.evNotifier(EventClass(EventEnum.TEAM_HAS_BALL, True))
            elif (
                not has_possession_now
                and self._bb.get(BlackboardKeys.ALGUEM_TEM_BOLA) == bob.robot_id.name
            ):
                self.eventManager.emit(
                    Event.BOB_LOST_BALL_POSSESSION, bob.robot_id.name
                )
                self.evNotifier(EventClass(EventEnum.TEAM_HAS_BALL, False))

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
