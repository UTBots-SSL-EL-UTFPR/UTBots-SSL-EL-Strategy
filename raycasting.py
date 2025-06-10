import math
import random
# LEMBRAR DE:
# Em atingiouRobo: iterar em cada um dos robôs, mas antes verificar se o raio refletiu em um robô e, se sim, pular a iteração nele
# Em atingiuRobo: Adicionar on raio à lista das reflexões
# Em menorCaminho: mudar o x0 e analisar todas as reflexões antes de verificar se existe alguma solução

# AINDA FALTA:
# Ver quais das soluções é a menor

YMAX_GOL = 0.5 #Segundo meu grSim
YMIN_GOL = -0.5
X_GOL = 2.250
RAIO_ROBO = 0.09
N_ROBOS = 3

class Raio:
    def __init__(self, angulo, trajetoria = None, refletir = None, robo = None):
        self.angulo = angulo
        if all(item in trajetoria for item in refletir):    # Só cria o atributo abaixo se a trajetória do raio estiver em refletir
            self.robo = robo # id do robo no qual refletiu

class Trajetoria:
    def __init__(self):
        self.raios = [] # Lista com todos os raios

def criaRaios (trajetorias, nraios, angulo_base):   # Cria uma lista com todos os raios iniciais
    for i in range (nraios):
        novo_raio = Raio(angulo_base*(i+1))
        nova_trajetoria = Trajetoria()
        nova_trajetoria.append(novo_raio)
        trajetorias.append(nova_trajetoria)

def entrouGol (nraios, solucoes, trajetorias, x0, y0):
    for i in range(nraios):
        angulo = trajetorias[i].raios[-1].angulo    # Acessa o último ângulo de cada uma das trajetórias
        if(angulo != math.pi/2 and angulo != math.pi*3/2):    # Se o ângulo for vertical, não há como cruzar a linha de trás do campo
            t = (X_GOL - x0) / math.cos(angulo)   # Descobre o parâmetro quando a bola cruza a linha do gol a partir da expressão x(t) = x_bola + t*cos()
            y = y0 + t * math.sin(angulo)    # Usa o parâmetro já calculado para encontrar onde o raio cruza o a linha de trás do gol
            if(y < YMAX_GOL and y > YMIN_GOL):      # Se ela estiver no intervalo do gol, então uma solução é encontrada
                solucoes.append(trajetorias[i]) # Salva a trajetória cujo último ângulo atravessa o gol

# Joga a expressão paramétrica do raio na expressão do círulo do robô. Simplificando fica t² + 2*(math.cos(angulo_base*(i+1))*(x_bola-x_robo) + math.sin(angulo_base*(i+1))(y_bola-y_robo))*t + x_bola*(x_bola - 2*x_raio) + y_bola*(y_bola - 2*y_raio) - RAIO_ROBO
def atingiuRobo (nraios, refletir, angulo_base, x0, y0):
    for i in range(nraios):
        for j in range (N_ROBOS):   # Vê se colide com cada um dos robôs
            xr = robo[j].x  # Precisa mudar pra como realmente a gente recebe essas coordenadas
            yr = robo[j].y
            a = 1
            b = 2*(math.cos(angulo_base*(i+1))*(x0-xr) + math.sin(angulo_base*(i+1))(y0-yr))
            c = x0*(x0 - 2*xr) + y0*(y0 - 2*y0) - RAIO_ROBO
            delta = b*b - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo

            if (delta >= 0):
                refletir.append((angulo_base*(i+1)))
         

def menorCaminho (x_bola, y_bola): #Parâmetros que serão recebidos do ssl_vision
    nraios = 360 # Exemplo
    solucoes = []   # Lista com os ângulos de todos os raios que passam pelo gol
    refletir = []   # Lista com os ângulos de todos os raios que passam pelo gol
    trajetorias = []    #Lista com todas as trejetorias
    angulo_base = 2*math.pi / nraios
    x0 = x_bola
    y0 = y_bola

    criaRaios(trajetorias, nraios, angulo_base)

    entrouGol(nraios, solucoes, trajetorias, x0, y0)
    if(len(solucoes) == 0):
        atingiuRobo (nraios, refletir, angulo_base, x0, y0)
    nrefl = len(refletir)
    if(nrefl != 0):
    # PROBLEMA: Como fazer os referenciais mudar e manter toda a trejetória de um raio?
        while(len(solucoes) == 0):  # Repete até que haja pelo menos um raio indo direto ao gol
            for i in range (nrefl):
                entrouGol(nraios, solucoes, angulo_base, x0, y0)
                if(len(solucoes) == 0):
                    atingiuRobo (nraios, refletir, angulo_base, x0, y0)     
       
