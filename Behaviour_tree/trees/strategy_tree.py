# trees/strategy_tree.py
#estrategia macro time
# trees/strategy_tree.py
import py_trees 
from .tree import Tree
from ..behaviors.strategy import conditions as condition_nodes
from ..behaviors.strategy import actions as action_nodes

from ..core.event_callbacks import BB_flags_and_values

contexts = BB_flags_and_values.Flags.Team_Flags.Context

class Strategy_tree(Tree):
    """
    Árvore de estratégia geral.
    V1.0
    - Usa Selector na raiz para escolher entre Ataque, Defesa e Bola Neutra, dependendo da posse
    - Cada ramo escreve um 'context' no blackboard, que representa um "estilo" de jogo
    """
    def __init__(self):
        super().__init__(name="StrategyTree")
        self.current_context = ""

    def create_tree(self) -> py_trees.behaviour.Behaviour:
        
        #---------------------------------------------------------------------#
        #                          TEMOS POSSE DE BOLA                        #
        #---------------------------------------------------------------------#
        with_ball_simple_attack = py_trees.composites.Sequence(
            name="Ball_possetion: Simple_attack", memory=False, children=[
                condition_nodes.is_simple_atack(), 
                action_nodes.Set_blackboard_value("context: simple atack",contexts.is_simple_atack, True)
            ]
        )

        with_ball_complex_attack = py_trees.composites.Sequence(
            name="Ball_possetion: Attack_from_recovery", memory=False, children=[
                condition_nodes.is_atack_from_recovery(),
                action_nodes.Set_blackboard_value("Context: recovery",contexts.is_atack_from_recovery, True)
            ]
        )
        with_ball_slow_attack = py_trees.composites.Sequence(
            name="Ball_possetion: with_ball_slow_attack", memory=False, children=[
                condition_nodes.is_slow_attack(),
                action_nodes.Set_blackboard_value("Context: slow_attack",contexts.is_slow_attack, True)
            ]
        )
        team_has_ball_branch = py_trees.composites.Selector("Team Has Ball", True, children=[with_ball_simple_attack, with_ball_complex_attack, with_ball_slow_attack])

        #---------------------------------------------------------------------#
        #                        NAO TEMOS POSSE DE BOLA                      #
        #---------------------------------------------------------------------#
        
        exemple_of_defense = py_trees.composites.Sequence(
            "exemple_defense",False, children=[
                condition_nodes.exemple_of_defense(),
                action_nodes.Set_blackboard_value("iniciar exemplo defesa",contexts.is_defense_exemple, True)
            ]
        )
        foes_has_ball_branch = py_trees.composites.Selector("foes Have Ball", True, children=[exemple_of_defense])

        

 #---------------------------------------------------------------------#
        #                      CRIAR OS RAMOS PRINCIPAIS                      #
        #---------------------------------------------------------------------#
        
        # Ramo de ataque: SE temos a bola, ENTÃO decidir qual ataque usar
        attack_logic_branch = py_trees.composites.Sequence(
            name="Attack Logic",
            memory=False,
            children=[
                condition_nodes.Team_Has_ball_posetion(), # Verifica a posse
                team_has_ball_branch                      # Executa o seletor de ataque
            ]
        )

        # Ramo de defesa: SE o adversário tem a bola, ENTÃO decidir qual defesa usar
        defense_logic_branch = py_trees.composites.Sequence(
            name="Defense Logic",
            memory=False,
            children=[
                condition_nodes.Foes_Have_ball_posetion(), # Verifica a posse do adversário
                foes_has_ball_branch                       # Executa o seletor de defesa
            ]
        )
        
        #---------------------------------------------------------------------#
        #                             NÓ RAIZ                                 #
        #---------------------------------------------------------------------#
        
        # O Root agora escolhe entre a LÓGICA DE ATAQUE ou a LÓGICA DE DEFESA
        root = py_trees.composites.Selector(
            name="StrategyRoot", 
            memory=False, 
            children=[attack_logic_branch, defense_logic_branch]
        )
        
        return root


if __name__ == "__main__":
    import py_trees.display

    tree = Strategy_tree()

    print("\n=== ESTRUTURA EM ASCII ===")
    print(py_trees.display.unicode_tree(tree.root))

    try:
        py_trees.display.render_dot_tree(tree.root, name="strategy_tree")
        print("\nArquivo DOT gerado como 'strategy_tree.dot' e imagem PNG correspondente.")
    except Exception as e:
        print(f"Não foi possível gerar DOT/PNG: {e}")
