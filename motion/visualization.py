import pygame
import sys
import random
from utils.pose2D import Pose2D  # Importa a classe Pose2D
from motion.veronoi import VoronoiGraph  # Certifique-se de que a classe VoronoiGraph está implementada corretamente no módulo motion.veronoi

# Para rodar usar o comando python3 -m motion.visualization
# com o terminal na pasta UTBots-SSL-EL-Strategy

# Gera pontos na borda da imagem, espaçados a cada n pixels
def gerar_pontos_borda(largura, altura, espacamento=50, limite_maximo=100):
    """
    Gera pontos na borda de uma área retangular.
    :param largura: Largura da área.
    :param altura: Altura da área.
    :param espacamento: Distância entre os pontos consecutivos.
    :param limite_maximo: Número máximo de pontos a serem gerados.
    :return: Lista de pontos na borda.
    """
    pontos_borda = []

    # Pontos na borda superior
    for x in range(0, largura + 1, espacamento):
        pontos_borda.append(Pose2D(x, 0))
        if len(pontos_borda) >= limite_maximo:
            return pontos_borda

    # Pontos na borda inferior
    for x in range(0, largura + 1, espacamento):
        pontos_borda.append(Pose2D(x, altura))
        if len(pontos_borda) >= limite_maximo:
            return pontos_borda

    # Pontos na borda esquerda
    for y in range(0, altura + 1, espacamento):
        pontos_borda.append(Pose2D(0, y))
        if len(pontos_borda) >= limite_maximo:
            return pontos_borda

    # Pontos na borda direita
    for y in range(0, altura + 1, espacamento):
        pontos_borda.append(Pose2D(largura, y))
        if len(pontos_borda) >= limite_maximo:
            return pontos_borda

    return pontos_borda

def visualisation():
    # Inicializa o Pygame
    pygame.init()

    # Tamanho da tela visível
    TELA_LARGURA = 4500 * 0.2
    TELA_ALTURA = 3000 * 0.2
    TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pygame.display.set_caption("Múltiplas Trajetórias")

    # Tamanho do mundo virtual
    MUNDO_LARGURA = 4500
    MUNDO_ALTURA = 3000
    
    # Gera os pontos na borda da imagem
    pontos_borda = gerar_pontos_borda(MUNDO_LARGURA, MUNDO_ALTURA, espacamento=200, limite_maximo=300)
    # Adiciona os pontos da borda à lista de pontos

    # Cores
    BRANCO = (255, 255, 255)
    VERMELHO = (255, 0, 0)
    VERDE = (0, 255, 0)
    AZUL = (0, 0, 255)
    LARANJA = (255, 165, 0)
    ROXO = (160, 32, 240)
    PRETO = (0, 0, 0)

    # Raio real dos elementos
    RAIO_REAL = 90
    RAIO_BOLA = 21.335

    # Fator de escala
    escala_x = TELA_LARGURA / MUNDO_LARGURA
    escala_y = TELA_ALTURA / MUNDO_ALTURA
    escala = min(escala_x, escala_y)

    # Número de pontos e inimigos
    NUM_PONTOS = 10
    NUM_BOBS_INIMIGOS = 3

    # Variáveis de controle
    linha_grossa = False
    ultima_tecla = False  # Variável para detectar clique único na tecla

    # Bobs inimigos (posicionados entre start_point e end_point)

    # Gera a posição aleatória da bola laranja
    bola_laranja_pos = Pose2D(
        random.randint(0, MUNDO_LARGURA),
        random.randint(0, MUNDO_ALTURA)
    )

    # Pontos de início e fim (fora do Voronoi)
    start_point = Pose2D(500, 1000)
    end_point = bola_laranja_pos

    # Gera os pontos dos Bobs inimigos com uma probabilidade de serem posicionados entre start_point e end_point
    pontosBobInimigos = []
    probabilidade_na_aresta = 0.5  # 70% de chance de estar na aresta
    
    for _ in range(NUM_BOBS_INIMIGOS):
        if random.random() < probabilidade_na_aresta:
            # Posiciona o Bob Inimigo ao longo da aresta
            t = random.uniform(0, 1)  # Fator aleatório entre 0 e 1
            x = start_point.x + t * (end_point.x - start_point.x)
            y = start_point.y + t * (end_point.y - start_point.y)
        else:
            # Posiciona o Bob Inimigo em uma posição aleatória no campo
            x = random.randint(90, MUNDO_LARGURA - 90)
            y = random.randint(90, MUNDO_ALTURA - 90)
        
        pontosBobInimigos.append(Pose2D(x, y))

    # Gera os pontos dos Bobs inimigos aleatórios (padrao)
    '''pontosBobInimigos = [
        Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))
        for _ in range(NUM_BOBS_INIMIGOS)
    ]'''

    # Inicializa a fonte para os números
    fonte = pygame.font.Font(None, 36)  # Fonte padrão com tamanho 36

    # Pontos iniciais do Voronoi
    points = pontosBobInimigos + pontos_borda  # Adiciona os pontos da borda
    
    pontos2 = [Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))]  # Lista vazia
    pontos3 = [Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))]  # Lista vazia

    if pontos2:
        points = points + [pontos2[0]]
    if pontos3:
        points = points + [pontos3[0]]


    # Cria o grafo baseado no diagrama de Voronoi
    voronoi_graph = VoronoiGraph(points) 

    # Adiciona os pontos de início e fim ao grafo
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    # Conecta diretamente start_point a end_point usando o novo método
    '''
    print("Chamando connect_external_points para conectar start e end")
    voronoi_graph.connect_external_points(start_point, end_point, "start", "end")
    '''
    # Encontra o menor caminho entre os dois pontos
    shortest_path_coords = voronoi_graph.find_shortest_path("start", "end")

    # Exibe os pontos do caminho como Pose2D
    for pose in shortest_path_coords:
        print(f"Pose2D(x={pose.x}, y={pose.y})")

    # Visualiza o grafo e o menor caminho
    voronoi_graph.visualize(start_point, end_point, shortest_path_coords)
    
    # Gera os pontos do caminho como Pose2D
    pontos1 = voronoi_graph.find_shortest_path("start", "end")
    

    
    
    # Função para desenhar uma trajetória com cor própria
    def desenhar_trajetoria(pontos, cor, largura):
        if not pontos:
            return  # Não faz nada se a lista estiver vazia
        ajustados = [(int(p.x * escala), int(p.y * escala)) for p in pontos]
        if len(ajustados) > 1:
            # Desenha o contorno preto da linha
            pygame.draw.lines(TELA, PRETO, False, ajustados, largura + 2)
            # Desenha a linha principal
            pygame.draw.lines(TELA, cor, False, ajustados, largura)
        
        # Adiciona círculos em todos os pontos com contorno preto
        for ponto in ajustados:
            if linha_grossa:
                # Contorno preto
                pygame.draw.circle(TELA, PRETO, ponto, int(RAIO_REAL * escala) + 2)
                # Círculo principal
                pygame.draw.circle(TELA, cor, ponto, int(RAIO_REAL * escala))

        for i, ponto in enumerate(ajustados):
            if i == 0:
                cor_ponto = VERDE
            elif i == len(ajustados) - 1:
                cor_ponto = VERMELHO
            else:
                cor_ponto = cor
            # Contorno preto para os círculos menores
            pygame.draw.circle(TELA, PRETO, ponto, 8)
            # Círculo menor principal
            pygame.draw.circle(TELA, cor_ponto, ponto, 6)

    # Carrega a imagem de fundo
    imagem_fundo = pygame.image.load("motion/campo.png")  
    imagem_fundo = pygame.transform.scale(imagem_fundo, (TELA_LARGURA, TELA_ALTURA))  # Redimensiona para o tamanho da tela

    # Loop principal
    clock = pygame.time.Clock()
    rodando = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Desenha a imagem de fundo
        TELA.blit(imagem_fundo, (0, 0))

        # Detecta o pressionamento da tecla L e alterna a grosso de linha uma única vez
        keys = pygame.key.get_pressed()
        if keys[pygame.K_l] and not ultima_tecla:
            linha_grossa = not linha_grossa  # Alterna entre True e False
            ultima_tecla = True  # Marca que a tecla foi pressionada

        if not keys[pygame.K_l]:
            ultima_tecla = False  # Reseta quando a tecla é liberada

        # Define a largura da linha
        largura_linha = 2 if not linha_grossa else int(RAIO_REAL / 2)  # Ajuste para uma largura de linha mais proporcional

        # Desenha as 3 trajetórias
        desenhar_trajetoria(pontos1, AZUL, largura_linha)
        desenhar_trajetoria(pontos2, VERDE, largura_linha)
        desenhar_trajetoria(pontos3, ROXO, largura_linha)

        # Adiciona círculos preenchidos nos pontos iniciais das listas com contorno preto
        if pontos1:  # Verifica se pontos1 não está vazio
            pygame.draw.circle(TELA, PRETO, (int(pontos1[0].x * escala), int(pontos1[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, AZUL, (int(pontos1[0].x * escala), int(pontos1[0].y * escala)), int(RAIO_REAL * escala))

        if pontos2:  # Verifica se pontos2 não está vazio
            pygame.draw.circle(TELA, PRETO, (int(pontos2[0].x * escala), int(pontos2[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, VERDE, (int(pontos2[0].x * escala), int(pontos2[0].y * escala)), int(RAIO_REAL * escala))

        if pontos3:  # Verifica se pontos3 não está vazio
            pygame.draw.circle(TELA, PRETO, (int(pontos3[0].x * escala), int(pontos3[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, ROXO, (int(pontos3[0].x * escala), int(pontos3[0].y * escala)), int(RAIO_REAL * escala))

        # Desenha os círculos dos Bobs inimigos com contorno preto
        for bob in pontosBobInimigos:
            pos = (int(bob.x * escala), int(bob.y * escala))
            pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala) + 2)  # Contorno preto
            pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala))  # Círculo principal

        # Desenha a bola laranja (ou verde) com contorno preto
        bola_pos_escalada = (int(bola_laranja_pos.x * escala), int(bola_laranja_pos.y * escala))
        pygame.draw.circle(TELA, PRETO, bola_pos_escalada, int(RAIO_BOLA * escala) + 2)  # Contorno preto (raio maior)
        pygame.draw.circle(TELA, LARANJA, bola_pos_escalada, int(RAIO_BOLA * escala))  # Bola principal

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    visualisation()
