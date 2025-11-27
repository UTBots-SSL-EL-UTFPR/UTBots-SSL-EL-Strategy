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


class EventEnum(StringEnum):
    VAZIO = ""
    TEAM_HAS_BALL = "teamHasBall"
    FOES_HAS_BALL = "foesHasBall"
    PASSA_MEIO = "passaMeio"
    HALT = "halt"
    TEAM_PENALTY = "teamPenalty"
    FOES_PENALTY = "foesPenalty"
    TEAM_FREE_KICK = "teamFreeKick"
    FOES_FREE_KICK = "foesFreeKick"
    STOP = "stop"
    KAMIJI_EXPULSO = f"0expulso"
    ARGENTON_EXPULSO = f"1expulso"
    SABADIN_EXPULSO = f"2expulso"


class TreePaths(StringEnum):
    KICKER = "kicker"
    SUPORT_OF = "suportOf"
    PIVO = "pivo"
    GOALKEEPER = "goalKeeper"
    DEF_RECUADO = "defRecuado"
    DEF_ADD = "def_add"
    BARRIER = "barrier"
    STOP1 = "stop1"
    STOP2 = "stop2"
    STOP3 = "stop3"
    HALT1 = "halt1"
    HALT2 = "halt2"
    HALT3 = "halt3"
    EXPULSO1 = "expulso1"
    EXPULSO2 = "expulso2"
    EXPULSO3 = "expulso3"


class EventClass:
    def __init__(self, name: EventEnum = EventEnum.VAZIO, value: bool | None = False):
        self.name: EventEnum = name
        self.value: bool = value


class BlackboardKeys(StringEnum):
    IS_PASS = "is_pass"
    VALID_LINE = "valide_line"
    UNMARKED_RECEIVER = "unmarked_receiver"
    IS_ATTACK_FROM_RECOVERY = "is_atack_from_recovery"
    IS_DEFENSE_EXEMPLE = "is_defense_exemple"
    IS_SLOW_ATTACK = "is_slow_attack"
    ALGUEM_TEM_BOLA = "alguem_tem_bola"

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

    BOB_GOT_BALL_POSSESSION = "got_ball_possession"
    BOB_LOST_BALL_POSSESSION = "lost_ball_possession"

    FOE_GOT_BALL_POSSESSION = "foes_got_ball_possession"
    FOE_LOST_BALL_POSSESSION = "foes_lost_ball_possession"

    BALL_REACHABLE = "ball_reachable"

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
@events.on(Event.BOB_GOT_BALL_POSSESSION)
def robot_got_posetion(robot_id: str):
    logger.warning("ROBOT %s got ball posetion", robot_id)

    _bb.set(f"{robot_id}{BlackboardKeys.HAS_BALL}", True)

    _bb.set(
        f"{BlackboardKeys.TEAM_HAS_BALL}",
        True,
    )
    _bb.set(BlackboardKeys.ALGUEM_TEM_BOLA, robot_id)
    (f"blackboard -> {_bb.get(BlackboardKeys.ALGUEM_TEM_BOLA)}")


@events.on(Event.BOB_LOST_BALL_POSSESSION)
def robot_lost_posetion(robot_id: str):
    logger.warning("ROBOT %s lost ball posetion", robot_id)

    _bb.set(f"{robot_id}{BlackboardKeys.HAS_BALL}", False)

    _bb.set(
        f"{BlackboardKeys.TEAM_HAS_BALL}",
        False,
    )

    _bb.set(f"{BlackboardKeys.ALGUEM_TEM_BOLA}", None)


# --------------------------------------------------------------------#


@events.on(Event.FOE_GOT_BALL_POSSESSION)
def foes_got_ball_posetion(robot_id: str):
    logger.debug("FOES got ball posetion")

    _bb.set(f"{BlackboardKeys.FOES_HAVE_BALL}", True)

    _bb.set(f"{BlackboardKeys.ALGUEM_TEM_BOLA}", robot_id)


@events.on(Event.FOE_LOST_BALL_POSSESSION)
def foes_lost_ball_posetion():
    logger.debug("lost ball posetion")

    _bb.set(f"{BlackboardKeys.FOES_HAVE_BALL}", False)

    _bb.set(f"{BlackboardKeys.ALGUEM_TEM_BOLA}", None)


# ----------------------------------target----------------------------------#


@events.on(Event.TARGET_REACHED)
def on_target_reached(robot_id: str):
    logger.debug("%s - %s = TRUE", robot_id, BlackboardKeys.TARGET_REACHED)
    _bb.set(f"{robot_id}{BlackboardKeys.TARGET_REACHED}", True)


@events.on(Event.TARGET_RESET)
def on_target_reset(robot_id: str):
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
