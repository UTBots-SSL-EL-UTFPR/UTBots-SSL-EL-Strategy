#teste passe

from Behaviour_tree.core.World_State import World_State, RobotID
from Behaviour_tree.robot.bob import Bob
import time
import py_trees as pt
from utils.pose2D import Pose2D
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.core import event_callbacks as callbacks
#NAOO ESTA PRONTO CORRIGIR OS ERROS 

from ....behaviors.common import condition as c_condition_nodes
from ....behaviors.strategy import actions as s_action_nodes 

from Behaviour_tree.positioning.positioning_helper import Positioning_helper
from Behaviour_tree.bob_manager import BobManager


TICK_INTERVAL = 0.1 

def main() -> None:
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    _bb = Blackboard_Manager.get_instance()
    

    kamiji = bob_state.get_bob(RobotID.Kamiji)
    defenser = bob_state.get_bob(RobotID.Defender)
    goalkeeper = bob_state.get_bob(RobotID.Goalkeeper)

    ph = Positioning_helper.get_object()

    if kamiji is None or defenser is None or goalkeeper is None: 
        print("Erro: Robôs não encontrados.")
        return

    # --- DEFINIÇÃO DAS ÁRVORES DE COMPORTAMENTO ---  )

    pass_sequence = pt.composites.Sequence(
        "Pass_Sequence",
        False,
        children=[           
            c_condition_nodes.Has_ball(),
            c_condition_nodes.Valid_Line(),
            c_condition_nodes.Receiver_Unmarked(),
            c_action_nodes.Choose_who_to_pass(),
            c_action_nodes.Align_for_pass(Robot=kamiji)
            c_action_nodes.execute_pass(),
            s_action_nodes.Set_blackboard_value("context:Pass",contexts.is_pass,True)
        ]
    )
    passer_tree = pt.trees.BehaviourTree(pass_sequence)
    passer_tree.setup(timeout=1.0) # Setup sem argumentos extras por enquanto

    # --- ÁRVORE DE COMPORTAMENTO DO RECEPTOR (Defensor) ---
    # Exatamente a árvore que você me mostrou antes
    receiver_positioning = pt.composites.Selector(
        "Position for Pass or Rebound",
        memory=False,
        children=[
            s_action_nodes.Receive_pass(name="Get_in_Pass_Position", robot=receiver),
            s_action_nodes.Rebound_position(name="Get_in_Rebound_Position", robot=receiver),
        ],
    )
    receiver_sequence = pt.composites.Sequence(
        "Decide and Move to Receive",
        memory=True,
        children=[
            receiver_positioning, 
            skill_action_nodes.Move_node(name="Move_to_Target", robot=receiver, target_pose_bb_key=f"{receiver.robot_id.name}_move_target")
        ],
    )
    receiver_tree = pt.trees.BehaviourTree(receiver_sequence)
    receiver_tree.setup(timeout=1.0)
    
    # --- ÁRVORE DO GOLEIRO (simples, só para ele não ficar parado) ---
    goalkeeper_sequence = pt.composites.Sequence(
        "Goalkeeper_Basic_Move", True, 
        [skill_action_nodes.Move_node("move goalkeeper", goalkeeper, 15)]
    )
    goalkeeper_tree = pt.trees.BehaviourTree(goalkeeper_sequence)
    goalkeeper_tree.setup(timeout=1.0)

    #-----------------------------------------------------------#
    # --- PREPARAÇÃO DO CENÁRIO NO GRSIM ---
    print("\n--- PREPARANDO O CENÁRIO PARA O TESTE DE PASSE ---")
    
    # Espere um pouco para o grSim carregar
    time.sleep(2) 
    wd.update()
    bob_state.update_all()

    # **MUITO IMPORTANTE**: Posicione a bola e os robôs manualmente para o teste
    # Você precisará de uma forma de setar essas posições no seu World_State ou diretamente no grSim
    # Exemplo (a forma de fazer isso pode variar no seu código):
    passer_start_pos = Pose2D(0, 0, 0) # Ex: Passador no centro
    receiver_start_pos = Pose2D(1500, 1000, 0) # Ex: Receptor na frente
    ball_start_pos = Pose2D(150, 0) # Bola um pouco na frente do passador
    
    # wd.set_robot_position(passer.robot_id, passer_start_pos) # Você precisa de uma função assim
    # wd.set_robot_position(receiver.robot_id, receiver_start_pos)
    # wd.set_ball_position(ball_start_pos)
    print(f"Cenário: Passador em {passer_start_pos}, Receptor em {receiver_start_pos}, Bola em {ball_start_pos}")

    # --- CONFIGURAÇÃO DO BLACKBOARD PARA INICIAR O PASSE ---
    # O gatilho principal para a jogada começar!
    pass_target_pose = Pose2D(2000, -1000) # Onde o passe DEVE ir
    
    _bb.set(f"{BB_flags_and_values.Flags.Team_Flags.kick_actions.team_kick}", True)
    _bb.set(f"{BB_flags_and_values.Values.Positions.pos_pass_target}", pass_target_pose)
    print(f"Blackboard: team_kick=True, Alvo do passe definido para {pass_target_pose}")
    
    #-----------------------------------------------------------#
    print("\n--- INICIANDO O LOOP DE TESTE ---")
    delay = 0.1
    t0 = time.time()

    while True:
        if time.time() >= delay + t0:
            wd.update()
            bob_state.update_all()

            # Executa a lógica de cada robô
            passer_tree.tick()
            receiver_tree.tick()
            goalkeeper_tree.tick()

            # Imprime informações úteis para debug
            print(f"Status da Seq. de Passe: {pass_sequence.status} | Pos Passador: {passer.state.position.to_tuple(True)}")
            print(f"Status da Seq. do Receptor: {receiver_sequence.status} | Pos Receptor: {receiver.state.position.to_tuple(True)}")
            
            t0 = time.time()

if __name__ == "__main__":
    main()
