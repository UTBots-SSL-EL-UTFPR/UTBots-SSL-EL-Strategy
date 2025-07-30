from core.event_manager import Event_Manager
from core.blackboard import Blackboard_Manager

from enum import Enum
#----------------------------------------------------------------------------#
#                                INSTRUÇÃO GERAL                             #
#----------------------------------------------------------------------------#
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
# COMO ADICIONAR UM NOVO EVENTO:
#   1. Registre-o no Enum `EventType`
#   2. Crie a função callback correspondente
#   3. Adicione a função em `subscribe_all()`
#
# PADRÃO: use nomes padronizados para facilitar leitura e manutenção

#----------------------------------------------------------------------------#
#                    Class enum para definir possiveis eventos               #
#----------------------------------------------------------------------------#
class EventType(Enum):
    ROBOT_STUCK = "robot_stuck"
    BALL_POSSESSION_CHANGE = "ball_possession_change"
    TARGET_REACHED = "target_reached"
    GOAL_OPEN = "goal_open"
    ENTERED_ZONE = "entered_zone"
    COLLISION_DETECTED = "collision_detected"
    PASS_RECEIVED = "pass_received"
    ...

#----------------------------------------------------------------------------#
#                                 CALLBACKS                                  #
#----------------------------------------------------------------------------#
_bb = Blackboard_Manager.get_instance()

def on_robot_stuck(robot_id):
    _bb.set(f"{robot_id.value}_is_stuck", True)

def on_target_reached(robot_id):
    _bb.set(f"{robot_id.value}_at_target", True)

def on_goal_open(robot_id):
    _bb.set("goal_open", True)

#----------------------------------------------------------------------------#
#                               super subscribe                              #
#----------------------------------------------------------------------------#

def subscribe_all():
    Event_Manager.subscribe(EventType.ROBOT_STUCK.value, on_robot_stuck)
    Event_Manager.subscribe(EventType.TARGET_REACHED.value, on_target_reached)
    Event_Manager.subscribe(EventType.GOAL_OPEN.value, on_goal_open)
