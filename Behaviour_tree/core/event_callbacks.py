from .event_manager import Event_Manager
from .blackboard import Blackboard_Manager

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
#               CLASSES PARA ACOMODAR FLAGS, MAIS FACIL DE USAR              #
#----------------------------------------------------------------------------#
class StaticBuilder:
    def __init__(self, path):
        self._path = path
    
    def __str__(self):
        return self._path
    
    def __repr__(self):
        return f"<Flag: '{self._path}'>"

class BB_flags_and_values:
    class Flags:
        class Team_Flags:
            class Context:
                is_simple_atack = StaticBuilder("is_simple_atack")
                is_atack_from_recovery = StaticBuilder("is_atack_from_recovery")
                is_defense_exemple = StaticBuilder("is_defense_exemple")
                is_slow_attack = StaticBuilder("is_slow_attack")
            class Ball_posetion:
                team_has_ball = StaticBuilder("team_has_ball")
                foes_have_ball = StaticBuilder("foes_have_ball")
        class motion:
            class ball:
                has_ball = StaticBuilder("has_ball")
                is_close = StaticBuilder("is_close")
            
            class navigation:
                target_reached = StaticBuilder("target_reached")
                path_blocked = StaticBuilder("path_blocked")
                is_stuck = StaticBuilder("is_stuck")
                lost_path = StaticBuilder("lost_path")
    class Values:
        class Positions:
            quadrant = StaticBuilder("quadrant")

#----------------------------------------------------------------------------#
#                                 CALLBACKS                                  #
#----------------------------------------------------------------------------#
_bb = Blackboard_Manager.get_instance()

def on_robot_stuck(robot_id):
    _bb.set(f"{robot_id.value}{BB_flags_and_values.Flags.motion.navigation.is_stuck}", True)

def on_target_reached(robot_id):
    _bb.set(f"{robot_id.value}{BB_flags_and_values.Flags.motion.navigation.target_reached}", True)

#----------------------------------------------------------------------------#
#                               super subscribe                              #
#----------------------------------------------------------------------------#

def subscribe_all():
    Event_Manager.subscribe(str(BB_flags_and_values.Flags.motion.navigation.is_stuck), on_robot_stuck)
    Event_Manager.subscribe(str(BB_flags_and_values.Flags.motion.navigation.target_reached), on_target_reached)
