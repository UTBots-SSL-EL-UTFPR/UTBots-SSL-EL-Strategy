import math
# AINDA FALTA:
# Em menorCaminho: mudar o x0 e analisar todas as reflexões antes de verificar se existe alguma solução
# Atualizar as trajetórias (Tá, mas um raio que reflete tem várias trajetórias, né? Usar recursão em menorCaminho é uma boa?)
# Ver quais das trajetórias é a menor (até agora só vê de um raio)
# Testar

YMAX_GOL = 0.5 #Segundo meu grSim
YMIN_GOL = -0.5
X_GOL = 2.250
Y_SUP = 1.500
RAIO_ROBO = 0.09
N_ROBOS = 3

class Raio:
    def __init__(self, angulo, trajetoria = None, refletir = None, robo = None, solucoes = None, x = None, y = None):
        self.angulo = angulo
        if refletir and trajetoria and trajetoria in refletir:    # Só cria o atributo abaixo se a trajetória do raio estiver em refletir
            self.robo = robo # id do robo no qual refletiu. Será que é necessário mesmo?
        if solucoes and trajetoria and trajetoria in solucoes:    # Só cria o atributo abaixo se a trajetoria for uma solução
            self.ponto_gol = (x, y) # Onde o raio atravessa o gol

    def __repr__(self):
        ponto_gol_str = getattr(self, 'ponto_gol', None)
        return f"Raio(angulo={self.angulo:.2f}, ponto_gol={ponto_gol_str})"

class Trajetoria:
    def __init__(self):
        self.raios = [] # Lista com todos os raios que compões a trajetoria

def criaRaios (trajetorias, nraios, angulo_base):   # Cria uma lista com todos os raios iniciais. Agora só está preenchido com os ângulos de cada raio
    for i in range (nraios):
        novo_raio = Raio(angulo_base*(i+1)) 
        nova_trajetoria = Trajetoria()
        nova_trajetoria.raios.append(novo_raio)
        trajetorias.append(nova_trajetoria)
    for t in trajetorias:
        print(t.raios)


def entrouGol (nraios, solucoes, trajetorias, x0, y0):
    for i in range(nraios):
        angulo = trajetorias[i].raios[-1].angulo    # Acessa o último ângulo de cada uma das trajetórias. Achei esse -1 meio feio
        if(angulo != math.pi/2 and angulo != math.pi*3/2):    # Se o ângulo for vertical, não há como cruzar a linha de trás do campo
            t = (X_GOL - x0) / math.cos(angulo)   # Descobre o parâmetro quando a bola cruza a linha do gol a partir da expressão x(t) = x_bola + t*cos()
            y = y0 + t * math.sin(angulo)    # Usa o parâmetro já calculado para encontrar onde o raio cruza o a linha de trás do gol
            if(y < YMAX_GOL and y > YMIN_GOL):      # Se ela estiver no intervalo do gol, então uma solução é encontrada
                solucoes.append(trajetorias[i]) # Salva a trajetória cujo último ângulo atravessa o gol
                trajetorias[i].raios[-1].ponto_gol = (X_GOL, y) # Salva o ponto onde o raio cruza o gol

# Joga a expressão paramétrica do raio na expressão do círulo do robô. Simplificando fica t² + 2*(math.cos(angulo)*(x_bola-x_robo) + math.sin(angulo)(y_bola-y_robo))*t + x_bola*(x_bola - 2*x_raio) + y_bola*(y_bola - 2*y_raio) - RAIO_ROBO
#def atingiuRobo (nraios, refletir, trajetorias, x0, y0):
 #   for i in range(nraios):
 #       angulo = trajetorias[i].raios[-1].angulo    # Acessa o último ângulo de cada uma das trajetórias (ou seja, só analisa o último raio)
 #       for j in range (N_ROBOS):   # Vê se colide com cada um dos robôs
 #           if(robo[j].x != x0 and robo[j].y):
 #               xr = robo[j].x  # EI, precisa mudar pra como realmente a gente recebe essas coordenadas
 #              yr = robo[j].y
 #               a = 1
 #               b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)(y0-yr))
 #               c = x0*(x0 - 2*xr) + y0*(y0 - 2*y0) - RAIO_ROBO
 #               delta = b*b - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo
 #
 #               if (delta >= 0):
 #                   refletir.append((trajetorias[i]))

def menorRaio(solucoes, x0, y0): # Vê qual das soluções tem o menor módulo. No momento é apenas um raio, mas o correto seria retornar um trajeotira completa
    menor = math.sqrt((2*X_GOL)*(2*X_GOL) + (2*Y_SUP)*(2*Y_SUP))    # Maior distância possível no campo (hipotenusa de um canto a outro)
    menor_trajetoria = None
    for trajetoria in solucoes:
        x = trajetoria.raios[-1].ponto_gol[0]  # Acessa as coordenadas do ponto do gol que o último raio da trajetória cruzou
        y = trajetoria.raios[-1].ponto_gol[1]

        distancia = math.sqrt((x - x0)*(x - x0) + (y - y0)*(y - y0))

        if(distancia < menor):
            menor_trajetoria = trajetoria.raios[-1].angulo

    return menor_trajetoria

        
def menorTrajetoria (): #Parâmetros que serão recebidos do ssl_vision. Mas o x e y da bola seriam apenas os parâmetros inciais, né?
    x0 = 0 # Exemplo
    y0 = 0
    nraios = 8 
    solucoes = []   # Lista com os ângulos de todos os raios que passam pelo gol
    # refletir = []   # Lista com os ângulos de todos os raios que passam pelo gol
    trajetorias = []    #Lista com todas as trejetorias
    angulo_base = 2*math.pi / nraios

    criaRaios(trajetorias, nraios, angulo_base)

    entrouGol(nraios, solucoes, trajetorias, x0, y0)
    #if(len(solucoes) == 0):
    #   atingiuRobo (nraios, refletir, trajetorias, x0, y0)

    menor_raio = menorRaio(solucoes, x0, y0) # Armazena a menor trajetória (no momento é apenas um raio que vai direto ao gol)

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

if __name__ == "__main__":
    menorTrajetoria()
