# ssl_robot_controller/behaviors/specific_roles/attacker_behaviors.py

import py_trees
from robot.bob import Bob
from ...behaviors.common.actions import move_to_position, kick_ball, Conduz_bola, Stop_robot, Set_posse_bola
from ...behaviors.common.condition import is_ball_visible, is_ball_reachable, is_goal_open, tem_posse_bola

class Attacker_tree(py_trees.behaviour.Behaviour):
    """
    Árvore do fodendo super bob.
    cada arvore tem sua "prioridade"
    pedi pro gepete dar um exemplo de "comportamento"
    a implementação é basicamente juntar os comportamentos acima de maneira que façam sentido
    quanto mais unitario e simples o comportamento, mais complexa e essa classe e mais refinado o controle do bob
    Prioridades: Atacar gol > Pegar bola > Posicionar-se
    """
    def __init__(self, name: str, robot_instance: Bob):
        super(Attacker_tree, self).__init__(name)
        self.robot = robot_instance

    def setup(self, timeout: float) -> bool:
        """
        Configura a árvore de comportamento do atacante.
        """
        # Criando a sub-árvore de ataque ao gol
        attack_goal_sequence = py_trees.composites.Sequence(
            name="Attack Goal Sequence", memory=True,
            children=[
                tem_posse_bola("Check Has Ball (Attack)", self.robot),
                is_goal_open("Check Goal Open"),
                kick_ball("Kick Ball to Goal", self.robot)
            ]
        )

        # Criando a sub-árvore para pegar a bola
        get_ball_sequence = py_trees.composites.Sequence(
            name="Get Ball Sequence", memory=True,
            children=[
                py_trees.decorators.Inverter(
                    name="NOT Has Ball (Get)",
                    child=tem_posse_bola("Check Has Ball (Get)", self.robot)
                ),
                is_ball_visible("Is Ball Visible (Get)"),
                py_trees.decorators.Inverter(
                    name="NOT Near Ball (Get)",
                    child=is_ball_reachable("Is Robot Near Ball (Get)", self.robot, threshold=0.3)
                ),
                move_to_position("Move to Ball", self.robot,
                               target_x=Field.get_ball_position()[0],
                               target_y=Field.get_ball_position()[1]),
                Set_posse_bola("Take Ball Possession (Sim)", self.robot, True) # Simula pegar a bola
            ]
        )

        # Criando a sub-árvore para driblar ou reposicionar
        # Uma vez que ele tem a bola, ele pode driblar ou se reposicionar para chutar
        dribble_or_reposition_sequence = py_trees.composites.Sequence(
            name="Dribble or Reposition Sequence", memory=True,
            children=[
                tem_posse_bola("Check Has Ball (Dribble/Reposition)", self.robot),
                py_trees.composites.Selector(
                    name="Dribble/Reposition Selector",
                    children=[
                        # Prioridade 1: Se o gol não está aberto, tentar driblar para melhor posição
                        py_trees.composites.Sequence(
                            name="If Goal Not Open, Dribble", memory=True,
                            children=[
                                py_trees.decorators.Inverter(
                                    name="Goal Not Open",
                                    child=IsGoalOpen("Is Goal Open (Dribble)")
                                ),
                                DribbleBall("Dribble for Position", self.robot),
                                move_to_position("Reposition for Shot", self.robot,
                                               target_x=world_model.get_ball_position()[0] + 0.2, # Exemplo de reposicionamento
                                               target_y=world_model.get_bPrioridades
                           target_x=world_model.get_robot_position(self.robot.robot_id)[0],
                           target_y=world_model.get_robot_position(self.robot.robot_id)[1]) # Posição padrão
        ]
        return True # setup bem-sucedido

    def update(self) -> py_trees.common.Status:
        """
        A árvore de comportamento do atacante é uma SubTree.
        Seus nós filhos são definidos no setup e o py_trees os gerencia.
        """
        # Como é uma SubTree, o update apenas passará o controle para seus filhos.
        # Não há lógica de update específica aqui além do que o py_trees faz.
        return self.status