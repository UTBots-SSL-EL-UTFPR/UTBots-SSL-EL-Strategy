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
