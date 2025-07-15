import math

# FOI FEITO NO ÚLTIMO DIA
    # Teste da menor solução
    # Teste da reflexão
    # Teste da interseção com os robôs inimigos
    # Teste da recursão
    
YMAX_GOL = 0.5      #Segundo meu grSim
YMIN_GOL = -0.5
X_GOL = 2.250
Y_SUP = 1.500
RAIO_ROBO = 0.09
N_ROBOS = 3

# Cria a classe Raio, composta pelo ângulo que ele faz com o eixo x+. Os atributos robo (robo no qual o raio reflete)
# e ponto_gol (ponto no qual o raio atravessa o gol) dependem da situação do jogo, portanto podem não existir
class Raio:
    def __init__(self, angulo, xr = None, yr = None, xf = None, yf = None):
        self.angulo = angulo
        self.refl = (xr, yr) 
        self.final = (xf, yf)

    def __repr__(self): # Serve só para a impressão do conteúdo (teste)
        xf, yf = self.final if self.final else (None, None)
        xr, yr = self.refl if self.refl else (None, None)
        return f"Raio(θ={self.angulo:.2f}, final=({xf}, {yf}), refl=({xr}, {yr}))"

 # Cria uma lista com todos os raios iniciais
def criaRaios (raios, nraios, angulo_base):  
    for i in range (nraios):
        novo_raio = Raio(angulo_base*(i+1)) 
        raios.append(novo_raio)

def ehRoboValido (coord_aliados, x0, y0, xa, ya, j):
    # Verifica se o robô em análise não é o robô que chuta a bola
    if ((x0 - 2*RAIO_ROBO < coord_aliados[j][0] < x0 + 2*RAIO_ROBO) and (y0 - 2*RAIO_ROBO < coord_aliados[j][1] < y0 + 2*RAIO_ROBO)):
        return False
    # Verifica se o robô em análise não é o robô que chutou a bola antes da reflexão
    if (xa != None and ya != None):
        if ((xa - 2*RAIO_ROBO < coord_aliados[j][0] < xa + 2*RAIO_ROBO) and (ya - 2*RAIO_ROBO < coord_aliados[j][1] < ya + 2*RAIO_ROBO)):
            return False
    return True

def atingiuInimigo (raios, x0, y0, coord_inimigos):
    for raio in raios[:]:   # Cria uma cópia da lista para evitar problemas de remoção durante a iteração
        angulo = raio.angulo
        for j in range (N_ROBOS):   # Vê se colide com cada um dos robôs
            if raio in raios:  # Verifica se o raio ainda está na lista (pode ter sido removido em aluma das iterações anteriores)
                xr = coord_inimigos[j][0]
                yr = coord_inimigos[j][1]
                a = 1
                b = 2*(math.cos(angulo)*(x0-xr) + math.sin(angulo)*(y0-yr))
                c = (x0 - xr)**2 + (y0-yr)**2 - RAIO_ROBO**2
                delta = b**2 - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo
                if (delta >= 0):
                    t1 = (-b + math.sqrt(delta)) / (2*a)
                    t2 = (-b - math.sqrt(delta)) / (2*a)
                    if (t1 >= 0 and t2 >= 0):  # Se ambos os tempos forem positivos, o raio atinge o robô
                        raios.remove(raio)    # Adiciona a lista o raio que reflete e as coordenadas do robô no qual bate

# Determina se a bola entrou no gol. Acessa o último ângulo de cada uma das trajetórias e analisa cada um deles. Se o raio for vertical, pula, pois não
# cruza nenhuma linha do gol. Descobre o parâmetro quando a bola cruza a linha do gol a partir da expressão x(t) = x_bola + t*cos()
#  e usa ele para encontrar onde o raio cruza o a linha de trás do gol. Salva a trajetória cujo último ângulo atravessa o gol e o ponto onde isso ocorre.
def entrouGol (solucoes, raios, x0, y0):
    for raio in raios:
        angulo = raio.angulo    
        if (angulo != math.pi/2 and angulo != math.pi*3/2):
            t = (X_GOL - x0) / math.cos(angulo)
            y = y0 + t * math.sin(angulo) 
            if ((y < YMAX_GOL and y > YMIN_GOL) and t >= 0):
                solucoes.append([raio])
                raio.final = (X_GOL, y)

# Joga a expressão paramétrica do raio na expressão do círulo do robô. Simplificando fica t² + 2*(math.cos(angulo)*(x_bola-x_robo) + math.sin(angulo)(y_bola-y_robo))*t + x_bola*(x_bola - 2*x_raio) + y_bola*(y_bola - 2*y_raio) - RAIO_ROBO
def atingiuAliado (refletiu, raios, x0, y0, coord_aliados, xa = None, ya = None):
    for raio in raios:
        angulo = raio.angulo    # Acessa o último ângulo de cada uma das trajetórias (ou seja, só analisa o último raio)
        for j in range (N_ROBOS):   # Vê se colide com cada um dos robôs
            if ehRoboValido(coord_aliados, x0, y0, xa, ya, j):
                xr = coord_aliados[j][0]
                yr = coord_aliados[j][1]
                a = 1
                b = 2*(math.cos(angulo)*(x0 - xr) + math.sin(angulo)*(y0 - yr))
                c = (x0 - xr)**2 + (y0 - yr)**2 - RAIO_ROBO**2
                delta = b**2 - 4*a*c # Se o delta for negativo, o raio não cruza a equação da circunferência do robo
                if (delta >= 0):
                    t1 = (-b + math.sqrt(delta)) / (2*a)
                    t2 = (-b - math.sqrt(delta)) / (2*a)
                    if (t1 >= 0 and t2 >= 0):  # Se ambos os tempos forem positivos, o raio atinge o robô
                        refletiu.append(raio)    # Adiciona a lista o raio que reflete e as coordenadas do robô no qual bate
                        raio.refl = (xr, yr)

# Vê qual das soluções tem o menor módulo
def menorSolucao(solucoes, x0, y0, nsol):
    # Contabiliza o comprimento de todas as trajetórias
    comprimentos = [0] * nsol
    for i in range(nsol):
        for raio in solucoes[i]:
            if raio.final and None not in raio.final:
                x = raio.final[0]
                y = raio.final[1]
            else:
                x = raio.refl[0]
                y = raio.refl[1]
            distancia = math.hypot(x - x0, y - y0)
            comprimentos[i] += distancia
    
    # Verirfica qual é a menor trajetória
    menor_trajetoria = solucoes[0]
    menor = comprimentos[0]
    for i in range(nsol):
        if (comprimentos[i] < menor):
            menor = comprimentos[i]
            menor_trajetoria = solucoes[i]

    return menor_trajetoria

# Cria varios raios que saem da bola. Depois de ver se algum acerta o gol, calcula o de menor módulo entre eles. Ainda falta adicionar osbtáculos (última coisa) e refletir quando bate em um aliado)        
def menorTrajetoria (x0, y0, coord_aliados, coord_inimigos, lim_refl, xa = None, ya = None): 
    nraios = 8 
    solucoes = []
    refletiu = []
    raios = []
    angulo_base = 2*math.pi / nraios

    # Irradia a partir do robô que chuta a bola
    criaRaios(raios, nraios, angulo_base)

    # Descarta raios que atingem os robôs inimigos e verifica se a bola entrou no gol ou se reflete
    atingiuInimigo (raios, x0, y0, coord_inimigos)
    entrouGol(solucoes, raios, x0, y0)    
    atingiuAliado (refletiu, raios, x0, y0, coord_aliados, xa, ya)

    # Se não houver soluções, verifica se algum raio refletiu e, através da recursão, analisa se há alguma
    # solução na última refleção. Se houver, junta os raios da trajetória
    if (len(solucoes) == 0):
        nrefl = len(refletiu)
        for i in range(nrefl):
            menor_caminho = None
            if (lim_refl < (N_ROBOS - 1)):  # Limita o nº de reflexões para que a bola não volte para algum robô que já jogou
                menor_caminho = menorTrajetoria(refletiu[i].refl[0], refletiu[i].refl[1], coord_aliados, coord_inimigos, lim_refl + 1, x0, y0)
            if (menor_caminho != None):
                trajetoria = []
                # A trajetória passa a ser o raio que refletiu mais a trajetória de menor módulo retornada da recursão
                trajetoria.append(refletiu[i])
                trajetoria += menor_caminho
                solucoes.append(trajetoria)

    nsol = len(solucoes)
    if (nsol != 0):
        # Se houver soluções, retorna a de menor módulo
        return menorSolucao(solucoes, x0, y0, nsol)
    return None

# TESTE
# Inicializando parâmetros que devem ser fornecidos pelo SSL vision, mas estou colocando aqui só para teste
# Coordenadas do robô que chuta a bola
#if __name__ == "__main__":
#    x0 = 0
#    y0 = 0
#    coord_aliados = [(0, 0), (1, 1), (1.5, 1)] # Matriz [N_ROBOS X 2]
#    coord_inimigos = [(0.5, 0), (1, -0.25), (1.5, 0.25)] # Matriz [N_INIMIGOS X 2]
#    for i, (x, y) in enumerate(coord_aliados): # Teste
#        print(f"Robô {i}: x = {x}, y = {y}")
#
#    print("Trajetória de menor módulo:", menorTrajetoria(x0, y0, coord_aliados, coord_inimigos, 0))
