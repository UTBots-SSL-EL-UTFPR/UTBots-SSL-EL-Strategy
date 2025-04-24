import pygame
import sys
import random

# Inicializa o Pygame
pygame.init()

# Tamanho da tela visível
TELA_LARGURA = 4500 * 0.3
TELA_ALTURA = 3000 * 0.3
TELA = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
pygame.display.set_caption("Múltiplas Trajetórias")

# Tamanho do mundo virtual
MUNDO_LARGURA = 4500
MUNDO_ALTURA = 3000

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

# Pontos das trajetórias
pontos1 = [(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA)) for _ in range(NUM_PONTOS)]
pontos2 = [(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA)) for _ in range(NUM_PONTOS)]
pontos3 = [(random.randint(0, MUNDO_LARGURA), random.randint(0, MUNDO_ALTURA)) for _ in range(NUM_PONTOS)]

# Bobs inimigos
pontosBobInimigos = [
    (random.randint(90, MUNDO_LARGURA - 90), random.randint(90, MUNDO_ALTURA - 90))
    for _ in range(NUM_BOBS_INIMIGOS)
]

# Gera a posição aleatória da bola laranja
bola_laranja_pos = (
    random.randint(0, MUNDO_LARGURA),
    random.randint(0, MUNDO_ALTURA)
)

# Inicializa a fonte para os números
fonte = pygame.font.Font(None, 36)  # Fonte padrão com tamanho 36

# Função para desenhar uma trajetória com cor própria
def desenhar_trajetoria(pontos, cor, largura):
    ajustados = [(int(x * escala), int(y * escala)) for x, y in pontos]
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
imagem_fundo = pygame.image.load("campo.png")  # Substitua "fundo.jpg" pelo nome do arquivo da sua imagem
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
    pygame.draw.circle(TELA, PRETO, (int(pontos1[0][0] * escala), int(pontos1[0][1] * escala)), int(RAIO_REAL * escala) + 2)
    pygame.draw.circle(TELA, AZUL, (int(pontos1[0][0] * escala), int(pontos1[0][1] * escala)), int(RAIO_REAL * escala))

    pygame.draw.circle(TELA, PRETO, (int(pontos2[0][0] * escala), int(pontos2[0][1] * escala)), int(RAIO_REAL * escala) + 2)
    pygame.draw.circle(TELA, VERDE, (int(pontos2[0][0] * escala), int(pontos2[0][1] * escala)), int(RAIO_REAL * escala))

    pygame.draw.circle(TELA, PRETO, (int(pontos3[0][0] * escala), int(pontos3[0][1] * escala)), int(RAIO_REAL * escala) + 2)
    pygame.draw.circle(TELA, ROXO, (int(pontos3[0][0] * escala), int(pontos3[0][1] * escala)), int(RAIO_REAL * escala))

    # Desenha os círculos dos Bobs inimigos com contorno preto
    for x, y in pontosBobInimigos:
        pos = (int(x * escala), int(y * escala))
        pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala) + 2)  # Contorno preto
        pygame.draw.circle(TELA, PRETO, pos, int(RAIO_REAL * escala))  # Círculo principal

    # Desenha a bola laranja (ou verde) com contorno preto
    bola_pos_escalada = (int(bola_laranja_pos[0] * escala), int(bola_laranja_pos[1] * escala))
    pygame.draw.circle(TELA, PRETO, bola_pos_escalada, int(RAIO_BOLA * escala) + 2)  # Contorno preto (raio maior)
    pygame.draw.circle(TELA, LARANJA, bola_pos_escalada, int(RAIO_BOLA * escala))  # Bola principal

    # Adiciona números aos pontos iniciais das trajetórias
    numeros = ["1", "2", "3"]
    posicoes_iniciais = [pontos1[0], pontos2[0], pontos3[0]]

    for i, pos in enumerate(posicoes_iniciais):
        texto = fonte.render(numeros[i], True, PRETO)  # Renderiza o número em preto
        texto_pos = (int(pos[0] * escala) - 10, int(pos[1] * escala) - 10)  # Ajusta a posição do texto
        TELA.blit(texto, texto_pos)  # Desenha o número na tela

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
