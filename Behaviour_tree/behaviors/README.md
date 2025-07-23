ESTTRUTURA BEHAVIOR TREE

BEHAVIORS
comportamentos dos bobs, implementam as "ideias" deles, eles se dividem em:
common -> todos fazem
"unicos" -> nao criei, mas seriam especificos de um bob (supomos que só de para fzr um chutador)

Nós em uma arvore
-> sao os behaviors, construimos a arvore associando pais e filhos
->dividem-se em nós de ação e de condição

Nós Compostos (py_trees.composites.)
fazem mais q uma ação ou condição, representam varias etapas
-. seletor -> funciona como um ou, tem um "fila" de açoes e tenta executar todas, caso uma funcione retorna sucesso
-. sequence -> uma sequencia de passos, serve para atingir um obj, retorna falha se um nó falhar
-> um exemplo seria chutar a bola, onde PRECISAMOS garantir varias etapas para poder chutar
-. parallel -> executa ações em ciclo, pode ter varios tipos de retorno com falhas e sucesso

Nós Decoradores (py_trees.decorators.)
só tem um filho, travam a execução até serem completados (achei parecido com flags)
-. Inverter -> inverte o status de retorno do filho (VIRA UMA FLAG)
-. repeater -> repete x vezes - Limiter -> limita o filho em x reps (ticks)
-. FaliureIsRunning -> converte falha em running

Ciclo de vida de Nós
o ciclo de vida de um nó sao as funções dele que sao chadas nos ticks
-. **init**(self, name) -> classe do nó
-. setup(self, timeout) -> arvore gerenciadora (prepara nó para iniciar, só uma vez)
-. initialise(self) -> chamado no primeiro tick e sempre que seu estatus nao for running, usado para redef vars e preparar a prox exec
-. update(self) -> principal metodo, exec todo tick enquanto estiver ativo. aqui a magica acontece (retorna sucesso, falha etc...)
-. terminate(self, new_status) -> chamado quando o nó nao esta em running, para açoes

TICK -> clock de arvore -> tree.tick()
-. nós definem qual filho sera ticado (depende da prioridade e tipo de no)
-.tick avança até chegar as folhas (behaviors)
-.exec update ao chegar na folha
-. caso algum nó tenha running como opc, ele também tera uma "memoria", onde enquanto ele nao for fechado, o tick sera feito a partir dele

#TODO 3. O py_trees.Blackboard: Compartilhando Conhecimento na Árvore

O Blackboard é um conceito fundamental em Behavior Trees para gerenciar e compartilhar dados entre os nós da árvore, sem a necessidade de passar argumentos explicitamente entre eles ou ter variáveis globais espalhadas. Pense nele como um quadro branco onde todos os nós podem ler e escrever informações.
Por que Usar o Blackboard?

    Compartilhamento de Estado: É o principal mecanismo para que um nó (ex: uma condição) grave informações (ex: ball_position) e outros nós (ex: uma ação de movimento) leiam essas informações para tomar decisões ou executar ações.
    Desacoplamento: Reduz o acoplamento entre os nós. Em vez de um nó precisar saber sobre a implementação interna de outro para obter dados, ele simplesmente acessa o Blackboard por uma chave.
    Persistência: O estado no Blackboard persiste entre os ticks da árvore, permitindo que informações calculadas em um tick sejam usadas em ticks subsequentes.
    Flexibilidade: Permite que você mude a lógica da árvore sem precisar alterar a interface de muitos nós folha, desde que a interface do Blackboard (as chaves usadas) permaneça consistente.

Quando Usar o Blackboard?

Você deve usar o Blackboard para qualquer informação que:

    Precise ser lida ou escrita por múltiplos nós em diferentes partes da árvore.
    Represente o estado do ambiente (posição da bola, objetos, obstáculos).
    Represente o estado interno do robô que precisa ser acessado globalmente (energia da bateria, posse da bola, objetivo atual).
    Seja o resultado de um cálculo de um nó que outro nó precisa.

Como Usar o Blackboard no py_trees:

Cada nó py_trees.behaviour.Behaviour possui um atributo self.blackboard, que é uma instância do py_trees.blackboard.Blackboard.
