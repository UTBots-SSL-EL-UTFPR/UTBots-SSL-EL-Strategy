import pygame
import sys
import random
from utils.pose2D import Pose2D
from motion.veronoi import VoronoiGraph
from motion.bestPath import BestPath

def visualisation():
    pygame.init()

    TELA_LARGURA = int(4500 * 0.2)
    TELA_ALTURA = int(3000 * 0.2)
    TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pygame.display.set_caption("Múltiplas Trajetórias")

    MUNDO_LARGURA = 4500
    MUNDO_ALTURA = 3000

    def gerar_pontos_borda(largura, altura, espacamento=50, limite_maximo=100):
        pontos_borda = []

        for x in range(0, largura + 1, espacamento):
            pontos_borda.append(Pose2D(x, 0))
            if len(pontos_borda) >= limite_maximo:
                return pontos_borda

        for x in range(0, largura + 1, espacamento):
            pontos_borda.append(Pose2D(x, altura))
            if len(pontos_borda) >= limite_maximo:
                return pontos_borda

        for y in range(0, altura + 1, espacamento):
            pontos_borda.append(Pose2D(0, y))
            if len(pontos_borda) >= limite_maximo:
                return pontos_borda

        for y in range(0, altura + 1, espacamento):
            pontos_borda.append(Pose2D(largura, y))
            if len(pontos_borda) >= limite_maximo:
                return pontos_borda

        return pontos_borda

    pontos_borda = gerar_pontos_borda(MUNDO_LARGURA, MUNDO_ALTURA, espacamento=200, limite_maximo=300)
    
    BRANCO = (255, 255, 255)
    VERMELHO = (255, 0, 0)
    VERDE = (0, 255, 0)
    AZUL = (0, 0, 255)
    LARANJA = (255, 165, 0)
    ROXO = (160, 32, 240)
    PRETO = (0, 0, 0)

    RAIO_REAL = 90
    RAIO_BOLA = 21.335

    escala_x = TELA_LARGURA / MUNDO_LARGURA
    escala_y = TELA_ALTURA / MUNDO_ALTURA
    escala = min(escala_x, escala_y)

    NUM_BOBS_INIMIGOS = 25

    linha_grossa = False
    exibir_bolinhas_intersecoes = True

    bola_laranja_pos = Pose2D(
        random.randint(0, MUNDO_LARGURA),
        random.randint(0, MUNDO_ALTURA)
    )

    start_point = Pose2D(500, 1000)
    end_point = bola_laranja_pos

    # Gera os Bobs inimigos (obstáculos)
    pontosBobInimigos = []
    for _ in range(NUM_BOBS_INIMIGOS):
        x = random.randint(90, MUNDO_LARGURA - 90)
        y = random.randint(90, MUNDO_ALTURA - 90)
        pontosBobInimigos.append(Pose2D(x, y))

    fonte = pygame.font.Font(None, 36)

    # Exemplos de listas
    pontos1 = [Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))]
    pontos2 = [Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))]
    pontos3 = [Pose2D(random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))]

    # Pontos para Voronoi
    points = pontosBobInimigos + pontos_borda
    if pontos1: points.append(pontos1[0])
    if pontos2: points.append(pontos2[0])
    if pontos3: points.append(pontos3[0])

    voronoi_graph = VoronoiGraph(points)
    voronoi_graph.add_point(start_point, "start")
    voronoi_graph.add_point(end_point, "end")

    # Encontra caminho de pontos1
    best_path = BestPath()


    # Em vez de um único end_point, crie três destinos distintos
    end_point1 = Pose2D(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA))
    end_point2 = Pose2D(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA))
    end_point3 = Pose2D(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA))

    if pontos1:
        obstacles_for_p1 = pontosBobInimigos[:]
        if pontos2: obstacles_for_p1.append(pontos2[0])
        if pontos3: obstacles_for_p1.append(pontos3[0])
        pontos1 = best_path.find_shortest_path(pontos1[0], end_point1, obstacles_for_p1, RAIO_REAL)

        # Print dos pontos de pontos1 no formato solicitado
        for p in pontos1:
            print(f"Pose2D({(p.x/1000) - 2.25},{(p.y/1000) - 1.5},0),")

    # Encontra caminho de pontos2
    if pontos2:
        obstacles_for_p2 = pontosBobInimigos[:]
        if pontos1: obstacles_for_p2.append(pontos1[0])
        if pontos3: obstacles_for_p2.append(pontos3[0])
        pontos2 = best_path.find_shortest_path(pontos2[0], end_point2, obstacles_for_p2, RAIO_REAL)

    # Encontra caminho de pontos3
    if pontos3:
        obstacles_for_p3 = pontosBobInimigos[:]
        if pontos1: obstacles_for_p3.append(pontos1[0])
        if pontos2: obstacles_for_p3.append(pontos2[0])
        pontos3 = best_path.find_shortest_path(pontos3[0], end_point3, obstacles_for_p3, RAIO_REAL)

    def desenhar_trajetoria(pontos, cor, largura, exibir_bolinhas):
        if not pontos:
            return
        ajustados = [(int(p.x * escala), int(p.y * escala)) for p in pontos]
        if len(ajustados) > 1:
            pygame.draw.lines(TELA, PRETO, False, ajustados, largura + 2)
            pygame.draw.lines(TELA, cor, False, ajustados, largura)
        if exibir_bolinhas:
            for ponto in ajustados:
                if linha_grossa:
                    pygame.draw.circle(TELA, PRETO, ponto, int(RAIO_REAL * escala) + 2)
                    pygame.draw.circle(TELA, cor, ponto, int(RAIO_REAL * escala))
        for i, ponto in enumerate(ajustados):
            if i == 0:
                cor_ponto = VERDE
            elif i == len(ajustados) - 1:
                cor_ponto = VERMELHO
            else:
                cor_ponto = cor
            if exibir_bolinhas or i in (0, len(ajustados) - 1):
                pygame.draw.circle(TELA, PRETO, ponto, 8)
                pygame.draw.circle(TELA, cor_ponto, ponto, 6)

    imagem_fundo = pygame.image.load("motion/campo.png")
    imagem_fundo = pygame.transform.scale(imagem_fundo, (TELA_LARGURA, TELA_ALTURA))

    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_k:
                    exibir_bolinhas_intersecoes = not exibir_bolinhas_intersecoes
                if evento.key == pygame.K_l:
                    linha_grossa = not linha_grossa

        TELA.blit(imagem_fundo, (0, 0))

        largura_linha = 2 if not linha_grossa else int(RAIO_REAL / 2)

        desenhar_trajetoria(pontos1, AZUL, largura_linha, exibir_bolinhas_intersecoes)
        desenhar_trajetoria(pontos2, VERDE, largura_linha, exibir_bolinhas_intersecoes)
        desenhar_trajetoria(pontos3, ROXO, largura_linha, exibir_bolinhas_intersecoes)

        if pontos1:
            pygame.draw.circle(TELA, PRETO, (int(pontos1[0].x * escala), int(pontos1[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, AZUL, (int(pontos1[0].x * escala), int(pontos1[0].y * escala)), int(RAIO_REAL * escala))
        if pontos2:
            pygame.draw.circle(TELA, PRETO, (int(pontos2[0].x * escala), int(pontos2[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, VERDE, (int(pontos2[0].x * escala), int(pontos2[0].y * escala)), int(RAIO_REAL * escala))
        if pontos3:
            pygame.draw.circle(TELA, PRETO, (int(pontos3[0].x * escala), int(pontos3[0].y * escala)), int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, ROXO, (int(pontos3[0].x * escala), int(pontos3[0].y * escala)), int(RAIO_REAL * escala))

        for bob in pontosBobInimigos:
            pos = (int(bob.x * escala), int(bob.y * escala))
            pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala) + 2)
            pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala))

        bola_pos_escalada = (int(bola_laranja_pos.x * escala), int(bola_laranja_pos.y * escala))
        pygame.draw.circle(TELA, PRETO, bola_pos_escalada, int(RAIO_BOLA * escala) + 2)
        pygame.draw.circle(TELA, LARANJA, bola_pos_escalada, int(RAIO_BOLA * escala))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    visualisation()
