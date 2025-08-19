#teste movimentação
from core.World_State import World_State, RobotID
from robot.bob import Bob

"""Testa a árvore de comportamento para movimentação do robô em quadrantes.

Este script é responsável por inicializar e executar um teste específico
da Árvore de Comportamento (Behavior Tree - BT) de um robô. O objetivo principal
é validar a lógica que comanda a movimentação do robô para pontos de destino
localizados em cada um dos quatro quadrantes de um plano cartesiano definido.

Objetivos do Teste:
-------------------
- Verificar se a BT consegue selecionar a sub-árvore correta com base no
  quadrante de destino.
- Garantir que as ações de movimentação (ex: "Mover para Ponto") são
  executadas corretamente.
- Validar as condições de sucesso e falha (ex: "Já está no quadrante?",
  "Caminho obstruído?").
- Avaliar o tempo e a precisão com que o robô atinge cada alvo.

O teste irá comandar o robô a se mover para o centro de cada quadrante
em uma sequência predefinida (ex: Q3 -> Q6 -> Q5 -> Q1) e registrará o sucesso
ou falha de cada tarefa.

Como Executar:
-------------
Execute o script diretamente a partir do terminal. Certifique-se de que o
ambiente de simulação do robô esteja ativo.

    $ python3 test_quadrant_behavior_tree.py

"""
import py_trees as pt
from ....behaviors.common import condition as condition_nodes
from ....behaviors.common import actions as action_nodes
from ...tree import Tree
class Test_tree(Tree):
    def __init__(self):
        super().__init__(name="StrategyTree")
        self.current_context = ""

    def crate_tree(self):
        root = pt.composites.Sequence(
            "andar de canto a canto",
            True,
            children=[]
        )
        

def main():
    robot = Bob(RobotID.Kamiji)
    
    while True:
        robot.update()
        print(robot.state.position)

if __name__ == "__main__":
    main()
