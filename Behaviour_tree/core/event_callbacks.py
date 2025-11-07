# ----------------------------------------------------------------------------#
#               CLASSES PARA ACOMODAR FLAGS, MAIS FACIL DE USAR              #
# ----------------------------------------------------------------------------#
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .blackboard import Blackboard_Manager

logger = logging.getLogger(__name__)


class StringEnum(str, Enum):
    """
    adaptacao enum para nao ter q ficar botando .name e .value
    """

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: '{self.value}'>"


class BlackboardKeys(StringEnum):
    IS_PASS = "is_pass"
    VALID_LINE = "valide_line"
    UNMARKED_RECEIVER = "unmarked_receiver"
    IS_ATTACK_FROM_RECOVERY = "is_atack_from_recovery"
    IS_DEFENSE_EXEMPLE = "is_defense_exemple"
    IS_SLOW_ATTACK = "is_slow_attack"

    TEAM_HAS_BALL = "team_has_ball"
    FOES_HAVE_BALL = "foes_have_ball"

    TEAM_KICK = "team_kick"
    TEAM_PASS = "team_pass"
    TEAM_PREPARING = "team_preparing"

    HAS_BALL = "has_ball"
    IS_REACHABLE = "is_reachable"
    BALL_VISIBLE = "ball_visible"

    TARGET_REACHED = "target_reached"
    PATH_BLOCKED = "path_blocked"
    IS_STUCK = "is_stuck"
    LOST_PATH = "lost_path"

    navigation = "navigation_flag"

    QUADRANT = "quadrant"
    ZONE = "zone"
    POS_BALL_VISIBLE = "pos_ball_visible"
    POS_PASS_TARGET = "pos_pass_target"


class Event(str, Enum):

    TEAM_GOT_BALL_POSSESSION = "team_got_ball_possession"
    TEAM_LOST_BALL_POSSESSION = "lost_ball_possession"
    FOES_GOT_BALL_POSSESSION = "foes_got_ball_possession"
    FOES_LOST_BALL_POSSESSION = "foes_lost_ball_possession"
    BALL_REACHABLE = "ball_reachable"

    GOT_BALL_POSSESSION = "got_ball_possession"
    LOST_BALL_POSSESSION = "lost_ball_possession"

    ROBOT_STUCK = "robot_stuck"
    TARGET_REACHED = "target_reached"
    TARGET_RESET = "target_reset"

    PASS = "pass"
    BALL_VISIBLE = "ball_visible"
    BALL_NOT_VISIBLE = "ball_not_visible"
    VALID_LINE = "valid_line"
    UNMARKED_RECEIVER = "unmarked_receiver"

    NEW_QUADRANT = "new_quadrant"
    NEW_ZONE = "new_zone"


# ----------------------------------------------------------------------------#
#                              EVENT_MANAGER                                  #
# ----------------------------------------------------------------------------#


class EventManager:

    _instance = None

    def __init__(self):
        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    @staticmethod
    def get_instance() -> "EventManager":
        if EventManager._instance is None:
            EventManager._instance = EventManager()
        return EventManager._instance

    def on(self, event: str | Event):
        """Decorator para registrar handlers de um evento."""
        key = event.value if isinstance(event, Enum) else str(event)

        def wrapper(func: Callable[..., Any]):
            self._listeners.setdefault(key, []).append(func)
            logger.debug(f"Handler '{func.__name__}' registrado para '{key}'")
            return func

        return wrapper

    def emit(self, event: str | Event, *args, **kwargs):
        """Emite um evento chamando todos os handlers registrados."""
        key = event.value if isinstance(event, Enum) else str(event)
        if key not in self._listeners:
            logger.debug(f"Sem listeners para '{key}'")
            return
        for func in list(self._listeners[key]):
            try:
                func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Erro executando handler '{func.__name__}' em '{key}': {e}"
                )


# ----------------------------------------------------------------------------#
#                                 CALLBACKS                                  #
# ----------------------------------------------------------------------------#

_bb = Blackboard_Manager.get_instance()
events = EventManager.get_instance()


# ----------------------------------ball posetion----------------------------------#
@events.on(Event.GOT_BALL_POSSESSION)
def robot_got_posetion(robot_id: str):
    logger.debug("ROBOT %s got ball posetion", robot_id)
    _bb.set(f"{robot_id}{BlackboardKeys.HAS_BALL}", True)


@events.on(Event.LOST_BALL_POSSESSION)
def robot_lost_posetion(robot_id: str):
    logger.debug("ROBOT %s lost ball posetion", robot_id)
    _bb.set(f"{robot_id}{BlackboardKeys.HAS_BALL}", False)


# --------------------------------------------------------------------#


@events.on(Event.TEAM_GOT_BALL_POSSESSION)
def team_got_ball_posetion():
    logger.debug("TEAM got ball posetion")
    _bb.set(
            f"{BlackboardKeys.TEAM_HAS_BALL}",
            True,
        )


@events.on(Event.TEAM_LOST_BALL_POSSESSION)
def lost_ball_posetion():
    logger.debug("lost ball posetion")
    _bb.set(f"{BlackboardKeys.TEAM_HAS_BALL}", False)


@events.on(Event.FOES_GOT_BALL_POSSESSION)
def foes_got_ball_posetion():
    logger.debug("FOES got ball posetion")
    _bb.set(
            f"{BlackboardKeys.FOES_HAVE_BALL}",
            True,
        )


@events.on(Event.FOES_LOST_BALL_POSSESSION)
def foes_lost_ball_posetion():
    logger.debug("lost ball posetion")
    _bb.set(f"{BlackboardKeys.FOES_HAVE_BALL}", False)


# ----------------------------------target----------------------------------#


@events.on(Event.TARGET_REACHED)
def on_target_reached(robot_id: str):
    logger.debug("%s - %s", robot_id, BlackboardKeys.TARGET_REACHED)
    _bb.set(f"{robot_id}{BlackboardKeys.TARGET_REACHED}", True)


@events.on(Event.TARGET_RESET)
def on_target_reset(robot_id: str):
    logger.debug("%s - %s", robot_id, BlackboardKeys.TARGET_REACHED)
    _bb.set(f"{robot_id}{BlackboardKeys.TARGET_REACHED}", False)


def on_ball_reachable(robot_id: str, value):
    _bb.set(f"{robot_id}{BlackboardKeys.IS_REACHABLE}", value)


def on_pass(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.IS_PASS}", True)


def on_ball_visible(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.BALL_VISIBLE}", True)


def on_valid_line(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.VALID_LINE}", True)


def unmarked_receiver(robot_id):
    _bb.set(
        f"{robot_id}{BlackboardKeys.UNMARKED_RECEIVER}",
        True,
    )


def on_ball_not_visible(robot_id, best_position):
    _bb.set(f"{robot_id}{BlackboardKeys.BALL_VISIBLE}", False)
    _bb.set(
        f"{robot_id}{BlackboardKeys.POS_BALL_VISIBLE}",
        best_position,
    )


def target_reset(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.TARGET_REACHED}", False)


def new_quadrant(robot_id, new_quadrant):
    _bb.set(f"{robot_id}{BlackboardKeys.QUADRANT}", new_quadrant)


def new_zone(robot_id, new_zone):
    _bb.set(f"{robot_id}{BlackboardKeys.ZONE}", new_zone)
