#teste movimentação
from core.World_State import World_State, RobotID
from robot.bob import Bob

from time import time, sleep
import py_trees as pt
from ....behaviors.common import condition as condition_nodes
from ....behaviors.common import actions as action_nodes
from trees.tree import Tree

#pequenas arvores que definem papeis e posicionamento dos bobs
#
#
# -------------------- PLAYS IDEPENDENTES DA ARVORE (REAGEM AO REFEREE) --------------------#


# ----------------------------------------------------- #
#                    BOLA PARADA DELES                  #
# ----------------------------------------------------- #

# Verifica: bola parada deles

# Objetivo: impedir chute e posicionar para previnir passe 

# Papéis: Barreira principal, Barreira suporte e GK.

# Sai quando: bola entra em jogo; cai para Mid/Low Block conforme a zona.

#TODO Acessar referee e verificar se eles ganharam bola parada 
#TODO implementar Posicionamento em bola parada
#TODO implementar sub_arvore BOLA PARADA em bob_trees


# ----------------------------------------------------- #
#                    BOLA PARADA NOSSA                  #
# ----------------------------------------------------- #

# Verifica: bola parada Nossa

# Objetivo: tentar chutar ou passe adiantado para chute

# Papéis: Barreira principal, Barreira suporte e GK.

# Sai quando: bola entra em jogo; cai para Mid/Low Block conforme a zona.

#TODO Acessar referee e verificar se eles ganharam bola parada 
#TODO implementar Posicionamento em bola parada
#TODO implementar sub_arvore BOLA PARADA em bob_trees


