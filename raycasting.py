import math

# AINDA FALTA:
    # Em menorCaminho: mudar o x0 e analisar todas as reflexões antes de verificar se existe alguma solução
    # Atualizar as trajetórias (Tá, mas um raio que reflete tem várias trajetórias, né? Usar recursão em menorCaminho é uma boa?)
    # Ver quais das trajetórias é a menor (até agora só vê de um raio)
    # Ver se um raio reflete em um inimigo
    # Será que não é legal mudar x0 e y0 para uma tupla?

# FOI FEITO NO ÚLTIMO DIA
    # Teste das funções criaRaios, entrouGol, menorTrajetoria, menorRaio, para uma situação sem obstáculos e sem reflexões
    # Início do algorítmo de reflexão da bola (acho que vou usar recursão...)

YMAX_GOL = 0.5 #Segundo meu grSim
YMIN_GOL = -0.5
X_GOL = 2.250
Y_SUP = 1.500
RAIO_ROBO = 0.09
N_ROBOS = 3

# Cria a classe Raio, composta pelo ângulo que ele faz com o eixo x+. Os atributos robo (robo no qual o raio reflete)
# e ponto_gol (ponto no qual o raio atravessa o gol) dependem da situação do jogo, portanto podem não existir
class Raio:
    def __init__(self, angulo, trajetoria = None, refletir = None, xr = None,yr = None, solucoes = None, x = None, y = None):
        self.angulo = angulo
        if refletir and trajetoria and trajetoria in refletir:
            self.robo = (xr, yr) 
        if solucoes and trajetoria and trajetoria in solucoes:
            self.ponto_gol = (x, y)

    def __repr__(self): # Serve só para a impressão do conteúdo (teste)
        ponto_gol_str = getattr(self, 'ponto_gol', None)
        return f"Raio(angulo={self.angulo:.2f}, ponto_gol={ponto_gol_str})"

# A trajetória é uma lista de raios (composta pelo primeiro raio e pelos refletidos)
class Trajetoria:
    def __init__(self):
        self.raios = []

 # Cria uma lista com todos os raios iniciais. Agora só está preenchido com os ângulos de cada raio
def criaRaios (trajetorias, nraios, angulo_base):  
    for i in range (nraios):
        novo_raio = Raio(angulo_base*(i+1)) 
        nova_trajetoria = Trajetoria()
        nova_trajetoria.raios.append(novo_raio)
        trajetorias.append(nova_trajetoria)

# Determina se a bola entrou no gol. Acessa o último ângulo de cada uma das trajetórias e analisa cada um deles. Se o raio for vertical, pula, pois não
# cruza nenhuma linha do gol. Descobre o parâmetro quando a bola cruza a linha do gol a partir da expressão x(t) = x_bola + t*cos()
#  e usa ele para encontrar onde o raio cruza o a linha de trás do gol. Salva a trajetória cujo último ângulo atravessa o gol e o ponto onde isso ocorre.
def entrouGol (nraios, solucoes, trajetorias, x0, y0):
    for i in range(nraios):
        angulo = trajetorias[i].raios[-1].angulo    
        if(angulo != math.pi/2 and angulo != math.pi*3/2):
            t = (X_GOL - x0) / math.cos(angulo)
            y = y0 + t * math.sin(angulo) 
            if((y < YMAX_GOL and y > YMIN_GOL) and t >= 0):
                solucoes.append(trajetorias[i])
                trajetorias[i].raios[-1].ponto_gol = (X_GOL, y)

# Joga a expressão paramétrica do raio na expressão do círulo do robô. Simplificando fica t² + 2*(math.cos(angulo)*(x_bola-x_robo) + math.sin(angulo)(y_bola-y_robo))*t + x_bola*(x_bola - 2*x_raio) + y_bola*(y_bola - 2*y_raio) - RAIO_ROBO
def atingiuRobo (nraios, refletiu, trajetorias, x0, y0, coord_aliados):
    for i in range(nraios):
        angulo = trajetorias[i].raios[-1].angulo    # Acessa o último ângulo de cada uma das trajetórias (ou seja, só analisa o último raio)
        for j in range (N_ROBOS):   # Vê se colide com cada um dos robôs
            # if(coord_aliados[j][0] != x0 and coord_aliados[j][1]):
            xr = coord_aliados[j][0]
            yr = coord_aliados[j][1]
            a = 1
            b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)*(y0-yr))
            c = x0*(x0 - 2*xr) + y0*(y0 - 2*yr) - RAIO_ROBO
            delta = b*b - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo
            # O CÁLCULO DE DELTA ESTÁ ERRADO
            print(delta)
            print()
            if (delta >= 0):
                refletiu.append((trajetorias[i]))    # Adiciona a lista o raio que reflete e as coordenadas do robô no qual bate
                trajetorias[i].raios[-1].robo = (xr, yr)

    for i, traj in enumerate(refletiu):
        raio = traj.raios[-1]
        print(f"Reflexão {i}: ângulo = {raio.angulo:.2f} rad, robô = {raio.robo}")


# Vê qual das soluções tem o menor módulo. No momento é apenas um raio, mas o correto seria retornar um trajeotira completa.
def menorRaio(solucoes, x0, y0):
    if(len(solucoes) == 0):
        return None
    menor = math.sqrt((2*X_GOL)*(2*X_GOL) + (2*Y_SUP)*(2*Y_SUP))    # Maior distância possível no campo (hipotenusa de um canto a outro)
    menor_trajetoria = None
    for trajetoria in solucoes:
        x = trajetoria.raios[-1].ponto_gol[0]  # Acessa as coordenadas do ponto do gol que o último raio da trajetória cruzou
        y = trajetoria.raios[-1].ponto_gol[1]

        distancia = math.sqrt((x - x0)*(x - x0) + (y - y0)*(y - y0))

        if(distancia < menor):
            menor_trajetoria = trajetoria
            menor = distancia

    return menor_trajetoria

# Cria varios raios que saem da bola. Depois de ver se algum acerta o gol, calcula o de menor módulo entre eles. Ainda falta adicionar osbtáculos (última coisa) e refletir quando bate em um aliado)        
def menorTrajetoria (x0, y0, coord_alidos): 
    nraios = 8 
    solucoes = []
    refletiu = []
    trajetorias = []
    angulo_base = 2*math.pi / nraios

    criaRaios(trajetorias, nraios, angulo_base)

    entrouGol(nraios, solucoes, trajetorias, x0, y0)
    #if(len(solucoes) == 0):
    atingiuRobo (nraios, refletiu, trajetorias, x0, y0, coord_aliados)

    menor_raio = menorRaio(solucoes, x0, y0)

    return menor_raio

    # Deixei pra deipois, está muito confuso. Até aqui fingirei que o primeiro raio já atingiu o gol (o que é bem provável) e nenhum mefletiu
    #nreflexoes = len(refletir)
    # PROBLEMA: Como fazer os referenciais mudarem e manter toda a trejetória de um raio?
    #if(nsolucoes == 0):  # Repete até que haja pelo menos um raio indo direto ao gol
        # Fazer uma recursão que vai ligar os menores caminhos que foram refletidos desde o último, que acerta o gol.
        # A ideia é adicionar à trajetória o menor caminho dos que refletiram.
        # add.trajetoria(menor trajetoria)
        # Daí novos raios serão criados a partir de um novo x0, y0
        # A recursão para quando caminhos que vão direto ao gol são encontrado. Nesse ponto, o código vê qual o menor e retorna para a chamada anterior, adicionando o menor raio calculado à trajetóriacione tanto como programa principal, quanto como módulo importável sem executar tudo automaticamente.

# Inicializando parâmetros que devem ser fornecidos pelo SSL vision, mas estou colocando aqui só para teste
if __name__ == "__main__":
    x0 = 0
    y0 = 0
    coord_aliados = [(-1, 1), (0.5, 2), (1, 0.5)] # Matriz [N_ROBOS X 2]
    for i, (x, y) in enumerate(coord_aliados): # Teste
        print(f"Robô {i}: x = {x}, y = {y}")
    menorTrajetoria(x0, y0, coord_aliados)
