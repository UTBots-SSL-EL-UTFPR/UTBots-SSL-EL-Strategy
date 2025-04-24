import pygame
import random
from scipy.spatial import Voronoi

def venoi():
    # Inicializa o Pygame
    pygame.init()

    # Configurações da tela visível
    TELA_LARGURA = 800
    TELA_ALTURA = 600
    TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pygame.display.set_caption("Diagrama de Voronoi")

    # Tamanho do mundo virtual
    MUNDO_LARGURA = 4500
    MUNDO_ALTURA = 3000

    # Fator de escala para ajustar o mundo virtual à tela visível
    escala_x = TELA_LARGURA / MUNDO_LARGURA
    escala_y = TELA_ALTURA / MUNDO_ALTURA
    escala = min(escala_x, escala_y)

    # Cores
    BRANCO = (255, 255, 255)
    PRETO = (0, 0, 0)
    VERDE = (0, 255, 0)
    VERMELHO = (255, 0, 0)
    CORES = [
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for _ in range(100)
    ]

    # Gera pontos aleatórios no espaço do mundo virtual
    NUM_PONTOS = 10
    pontos = [(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA)) for _ in range(NUM_PONTOS)]

    # Define os pontos especiais (inicial e final)
    ponto_inicial = (random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA))
    ponto_final = (random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA))

    # Adiciona os pontos especiais à lista de pontos
    pontos.append(ponto_inicial)
    pontos.append(ponto_final)

    # Função para desenhar o diagrama de Voronoi
    def desenhar_voronoi(voronoi):
        # Desenha os pontos
        for ponto in pontos:
            ponto_escalado = (int(ponto[0] * escala), int(ponto[1] * escala))
            pygame.draw.circle(TELA, PRETO, ponto_escalado, 5)  # Desenha os pontos

        # Desenha as arestas do diagrama de Voronoi
        for aresta in voronoi.ridge_vertices:
            if -1 not in aresta:  # Ignora arestas infinitas
                ponto1 = tuple(map(int, voronoi.vertices[aresta[0]] * escala))
                ponto2 = tuple(map(int, voronoi.vertices[aresta[1]] * escala))
                pygame.draw.line(TELA, PRETO, ponto1, ponto2, 2)

        # Desenha os pontos especiais (inicial e final)
        inicial_escalado = (int(ponto_inicial[0] * escala), int(ponto_inicial[1] * escala))
        final_escalado = (int(ponto_final[0] * escala), int(ponto_final[1] * escala))
        pygame.draw.circle(TELA, VERDE, inicial_escalado, 10)  # Ponto inicial (verde)
        pygame.draw.circle(TELA, VERMELHO, final_escalado, 10)  # Ponto final (vermelho)

    # Loop principal
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Preenche o fundo
        TELA.fill(BRANCO)

        # Gera o diagrama de Voronoi
        voronoi = Voronoi(pontos)

        # Desenha o diagrama de Voronoi
        desenhar_voronoi(voronoi)

        # Atualiza a tela
        pygame.display.flip()

    # Encerra o Pygame
    pygame.quit()

if __name__ == '__main__':
    venoi()