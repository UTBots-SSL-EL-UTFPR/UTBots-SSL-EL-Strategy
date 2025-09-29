# ----------------------------------------------------------------------------#
#               CLASSES PARA ACOMODAR FLAGS, MAIS FACIL DE USAR              #
# ----------------------------------------------------------------------------#
import logging
from enum import Enum

from .blackboard import Blackboard_Manager
from .test_World_State import RobotID

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------#
#                                INSTRUÇÃO GERAL                             #
# ----------------------------------------------------------------------------#
# O sistema se baseia em callbacks (funções chamadas por eventos).
# A árvore de comportamento NÃO lê diretamente do Field, mas sim da Blackboard.
#
# A Blackboard (py_trees) atua como um repositório de flags de alto nível.
# Exemplo:
#  - O BobState do atacante detecta posição (500, 100)
#  - Em vez de armazenar diretamente a posição, disparamos um evento como:
#       "attacker_on_1st_quadrant"
#  - O callback correspondente define a flag no Blackboard:
#       Blackboard.set("ATTACKER_on_1st_quadrant", True)
#
# PADRÃO: use nomes padronizados para facilitar leitura e manutenção


class StringEnum(str, Enum):
    """
    adaptacao enum para nao ter q ficar botando .name e .value
    """

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self):
        return f"<{self.__class__.__name__}.{self.name}: '{self.value}'>"


class BlackboardKeys:
    class Flags:
        class TeamContext(StringEnum):
            IS_SIMPLE_ATTACK = "is_simple_atack"
            IS_PASS = "is_pass"
            VALID_LINE = "valide_line"
            UNMARKED_RECEIVER = "unmarked_receiver"
            IS_ATTACK_FROM_RECOVERY = "is_atack_from_recovery"
            IS_DEFENSE_EXEMPLE = "is_defense_exemple"
            IS_SLOW_ATTACK = "is_slow_attack"

        class BallPossession(StringEnum):
            TEAM_HAS_BALL = "team_has_ball"
            FOES_HAVE_BALL = "foes_have_ball"

        class KickActions(StringEnum):
            TEAM_KICK = "team_kick"
            TEAM_PASS = "team_pass"
            TEAM_PREPARING = "team_preparing"

        class BallMotion(StringEnum):
            HAS_BALL = "has_ball"
            IS_REACHABLE = "is_reachable"
            BALL_VISIBLE = "ball_visible"

        class Navigation(StringEnum):
            TARGET_REACHED = "target_reached"
            PATH_BLOCKED = "path_blocked"
            IS_STUCK = "is_stuck"
            LOST_PATH = "lost_path"

    class Values:
        class Positions(StringEnum):
            QUADRANT = "quadrant"
            ZONE = "zone"
            POS_BALL_VISIBLE = "pos_ball_visible"
            POS_PASS_TARGET = "pos_pass_target"


# ----------------------------------------------------------------------------#
#                                 CALLBACKS                                  #
# ----------------------------------------------------------------------------#

_bb = Blackboard_Manager.get_instance()


# ----------------------------------ball posetion----------------------------------#
def team_got_ball_posetion(robot_id: str):
    logger.debug("TEAM got ball posetion")

    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.HAS_BALL}", True)
    _bb.set(
        f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}",
        True,
    )
    _bb.set(
        f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}",
        False,
    )


def lost_ball_posetion(robot_id: str):
    logger.debug("lost ball posetion")
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.HAS_BALL}", False)
    aux = False
    for i in RobotID:
        if _bb.get(f"{i.name}{BlackboardKeys.Flags.BallMotion.HAS_BALL}"):
            aux = True
    
    if not aux:
        _bb.set(
            f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}",
            False,
        )
    _bb.set(
        f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}",
        False,
    )


def foes_got_ball_posetion(robot_id: str):
    logger.debug("FOES got ball posetion")

    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.HAS_BALL}", False)
    _bb.set(
        f"{BlackboardKeys.Flags.BallPossession.TEAM_HAS_BALL}",
        False,
    )
    _bb.set(
        f"{BlackboardKeys.Flags.BallPossession.FOES_HAVE_BALL}",
        True,
    )


def on_ball_reachable(robot_id: str, value):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.IS_REACHABLE}", value)


# ----------------------------------   MOTION   ----------------------------------#


def on_robot_stuck(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.Navigation.IS_STUCK}", True)


def on_pass(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.TeamContext.IS_PASS}", True)


def on_ball_visible(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.BALL_VISIBLE}", True)


def on_valid_line(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.TeamContext.VALID_LINE}", True)


def unmarked_receiver(robot_id):
    _bb.set(
        f"{robot_id}{BlackboardKeys.Flags.TeamContext.UNMARKED_RECEIVER}",
        True,
    )


def on_ball_not_visible(robot_id, best_position):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.BallMotion.BALL_VISIBLE}", False)
    _bb.set(
        f"{robot_id}{BlackboardKeys.Values.Positions.POS_BALL_VISIBLE}",
        best_position,
    )


def on_target_reached(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.Navigation.TARGET_REACHED}", True)


def target_reset(robot_id):
    _bb.set(f"{robot_id}{BlackboardKeys.Flags.Navigation.TARGET_REACHED}", False)


def new_quadrant(robot_id, new_quadrant):
    _bb.set(f"{robot_id}{BlackboardKeys.Values.Positions.QUADRANT}", new_quadrant)


def new_zone(robot_id, new_zone):
    _bb.set(f"{robot_id}{BlackboardKeys.Values.Positions.ZONE}", new_zone)
