# Behaviour_tree/trees/ofensive_sup/test_off_sup.py
import logging
import time

from .defender.defender_tree import get_defender_tree
from .suporte_recuado.suporte_recuado import get_pivo_tree

from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BlackboardKeys
from Behaviour_tree.core.World_State import TeamID, World_State
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.robot.FoesManager import FoesManager
from utils.pose2D import Pose2D

from ..helpers.field_helper import FieldHelper
from .goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from .ofensive_sup.offensive_suport_tree import get_off_sup_tree

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
# ==============================================================================#
# BLOCO DE TESTE                                                                #
# ==============================================================================#


def create_bobs():
    a = Bob(TeamID.Kamiji)
    b = Bob(TeamID.Argenton)
    c = Bob(TeamID.SabKawa)
    a.state.reset()
    b.state.reset()
    c.state.reset()
    return a, b, c


def create_scenario(all_bobs: list[Bob]):
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    # --- INICIALIZAR LEITURAS DA WORLD STATE --- #
    delay = 2
    t0 = time.time()
    while time.time() <= delay + t0:
        wd.update()
        for bob in all_bobs:
            bob.update()
    logger.info("Inicio")
    print("-" * 100)
    return


# EXECUTAR - # python3.10 -m Behaviour_tree.trees.ofensive_sup.test_off_sup

if __name__ == "__main__":
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()

    foes = FoesManager()
    kamiji, argenton, goalkeeper = create_bobs()
    all_bobs = [kamiji, argenton, goalkeeper]

    goalkeeper_tree = get_goalkeeper_tree(goalkeeper)

    defensor_kamiji_tree = get_defender_tree(kamiji)
    defensor_argenton_tree = get_defender_tree(argenton)

    pivo_kamiji_tree = get_pivo_tree(kamiji)
    pivo_argenton_tree = get_pivo_tree(argenton)

    offSup_kamiji_tree = get_off_sup_tree(kamiji)
    offSup_argenton_tree = get_off_sup_tree(argenton)

    create_scenario(all_bobs)
    update_delay = 0.001
    print_delay = 0.5
    tPrint = time.time()
    tUpdate = time.time()
    while True:
        if time.time() >= update_delay + tUpdate:
            wd.update()
            foes.update()
            for bob in all_bobs:
                bob.update()
            tUpdate = time.time()
            goalkeeper_tree.tick()

            """
            ATE AQUI TAVA DO JEITO Q VC DEIXOU O EXECUTE.PY ARGENTON, 
            DAQUI PRA FRENTE EU VOU SO DEIXAR PRONTO TODOS OS ESTADOS PRA VC
            COLOCAR AS PLAYS, VC CONHECE ELAS MELHOR DOQ EU
            """
            gc_state = (_bb.get("gc_state") or "stop").lower()

            # decide a play de acordo com o estado do referee q ta escrito no blackboard
            if gc_state == "halt":
                #a play do halt aqi
                pass

            elif gc_state == "stop":
                #a play do stop aqui
                pass

            elif gc_state in ("ready_kickoff_us"):
                #play de cobrar o kickoff nosso (kickoff é o ponta pe inicial no inicio do tempo)
                pass

            elif gc_state in ("ready_kickoff_them"):
                #play dos adversarios cobrando o kickoff deles (pode ser so o nosso stop msm)
                pass

            elif gc_state in ("ready_freekick_us",):
                #play da gente cobrando freekick
                pass

            elif gc_state in ("ready_freekick_them",):
                #eles cobrando free kick (n sei se tem barreira feita, mas se tiver vai ser nesse estado)
                pass
            elif gc_state == "ready_penalty_us":
                #penalti nosso
                pass
            elif gc_state == "ready_penalty_them":
                #penalti deles
                pass
            elif gc_state in ("ball_placement_us", "ball_placement_them"):
                #esse aqui nem tem na SSL-EL, mas ta no livro de regras ent deixa com pass aqui msm
                pass
            elif gc_state == "running":
                #AQUI É O JOGO RODANDO NORMAL, A PLAY DE NOS JOGANDO BOLA TEM Q SER NO ESTADO RUNNING
                pass

            else:
                #no else eu colocaria no stop so por seguranca
                pass
