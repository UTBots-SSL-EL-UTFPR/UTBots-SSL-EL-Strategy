import py_trees
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.core.blackboard import Blackboard_Manager
from Behaviour_tree.bob_manager import BobManager


from Behaviour_tree.commom_behaviours import condition as condition_nodes
from Behaviour_tree.commom_behaviours import actions as action_nodes



class PassTree:
    """
    Árvore de comportamento para a tática de passe.
    """

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id
        self.bob_manager = BobManager.get_object()
        self.robot = self.bob_manager.get_bob(self.robot_id)
        
        if self.robot is None:
            raise ValueError(f"Robô com ID {robot_id} não encontrado.")

    def create_tree(self) -> py_trees.behaviour.Behaviour:
        """
        Cria a árvore de comportamento para a tática de passe.
        """
        # Garante que temos um objeto de robô válido para passar aos nós
        if not self.robot:
            return py_trees.behaviours.Failure("Robô não inicializado")

        # ---------------------------------------------------------------------#
        #                          CONDIÇÕES                                   #
        # ---------------------------------------------------------------------#
        has_ball = condition_nodes.HasBall(robot=self.robot, name="Tem a Bola")
        valid_line = condition_nodes.ValidLine(name="Linha Válida")
        receiver_unmarked = condition_nodes.ReceiverUnmarked(name="Receptor Desmarcado")

        # ---------------------------------------------------------------------#
        #                          AÇÕES                                       #
        # ---------------------------------------------------------------------#
        choose_who_to_pass = action_nodes.ChooseWhoToPass(robot=self.robot, name="Escolhe Receptor")
        align_for_pass = action_nodes.AlignForPass(robot=self.robot, name="Alinha para Passe")
        execute_pass = action_nodes.ExecutePass(robot=self.robot, name="Executa Passe")
        
        # ---------------------------------------------------------------------#
        #                          NÓ RAIZ                                     #
        # ---------------------------------------------------------------------#

        # A tática de passe é uma sequência de passos
        root = py_trees.composites.Sequence(
            name="Pass Tactic Root",
            memory=True,  
            children=[
                has_ball,
                choose_who_to_pass,
                receiver_unmarked,
                valid_line,
                align_for_pass,
                execute_pass,
            ],
        )

        return root


# ==============================================================================#
# BLOCO DE VISUALIZAÇÃO (para rodar este arquivo diretamente)                   #
# ==============================================================================#

if __name__ == "__main__":
    import py_trees.display

    passer_robot_id = RobotID.Kamiji 
    pass_tree_builder = PassTree(robot_id=passer_robot_id)
    tree = pass_tree_builder.create_tree()

    print("\n=== ESTRUTURA DA ÁRVORE DE PASSE  ===")
    print(py_trees.display.unicode_tree(tree))

    #
    try:
        py_trees.display.render_dot_tree(tree, name="pass_tree")
        print("\nArquivo 'pass_tree.dot' e 'pass_tree.png' gerados com sucesso.")
    except Exception as e:
        print(f"\nNão foi possível gerar a imagem da árvore: {e}")