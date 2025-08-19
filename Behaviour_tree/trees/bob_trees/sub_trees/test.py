#teste movimentação
from core.World_State import World_State, RobotID
from robot.bob import Bob

from time import time, sleep
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

TICK_INTERVAL = 0.1  # X = 100ms. A árvore será chamada 10 vezes por segundo.
UPDATE_INTERVAL = TICK_INTERVAL / 2  # X/2 = 50ms. O robô será atualizado 20 vezes por segundo.

class Test_tree(Tree):
    def __init__(self):
        super().__init__(name="test")
        self.current_context = ""

    def create_tree(self):
        root = pt.composites.Sequence(
            "andar de canto a canto",
            True,
            children=[]
        )
        return root
        

def main():
    robot = Bob(RobotID.Kamiji)
    tree = Test_tree()
    root = tree.create_tree()
    delta = time()
    while True:
        
        loop_start_time = time.time()
        robot.update()

        print(f"Posição do Robô: {robot.state.position}")
        if iteration_counter % 2 == 0:
            print("--- Tick da Árvore ---")
            root.tick()
        iteration_counter += 1

        execution_time = time.time() - loop_start_time
        
        sleep_time = UPDATE_INTERVAL - execution_time
        
        if sleep_time > 0:
            time.sleep(sleep_time)
        

if __name__ == "__main__":
    main()
