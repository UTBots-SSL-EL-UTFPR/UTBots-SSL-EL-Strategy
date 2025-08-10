# defines.py - Constantes globais do projeto

# ============================================
# CONSTANTES DO CAMPO SSL
# ============================================
# Dimensões do campo (em milímetros, conforme SSL)
FIELD_X = 12000  # mm (12 metros) - comprimento
FIELD_Y = 9000    # mm (9 metros) - largura

# Robôs e bola
BOB_RADIUS = 0.09  # Raio do robô Bob em metros
BALL_RADIUS = 0.021  # Raio da bola em metros
BALL_POSSESSION_DISTANCE = BOB_RADIUS + BALL_RADIUS + 0.01  # Distância de posse da bola

# ============================================
# QUADRANTES DO CAMPO
# Campo SSL dividido em 12 quadrantes (4 horizontais x 3 verticais)
# Coordenadas: X vai de -6000 a +6000, Y vai de -4500 a +4500

#    -6000    -3000     0      +3000   +6000
#      |        |       |        |       |
# +4500+--------+-------+--------+-------+ +4500
#      |   Q1   |  Q2   |   Q3   |  Q4   |
# +1500+--------+-------+--------+-------+ +1500
#      |   Q5   |  Q6   |   Q7   |  Q8   |
# -1500+--------+-------+--------+-------+ -1500
#      |   Q9   |  Q10  |  Q11   |  Q12  |
# -4500+--------+-------+--------+-------+ -4500
#    -6000    -3000     0      +3000   +6000
#
r
# Definições dos quadrantes

# Quadrantes individuais (x_min, x_max, y_min, y_max)
QUADRANT_1 = (-6000, -3000, 1500, 4500)   # Superior esquerdo
QUADRANT_2 = (-3000, 0, 1500, 4500)       # Superior meio-esquerdo
QUADRANT_3 = (0, 3000, 1500, 4500)        # Superior meio-direito
QUADRANT_4 = (3000, 6000, 1500, 4500)     # Superior direito

QUADRANT_5 = (-6000, -3000, -1500, 1500)  # Meio esquerdo
QUADRANT_6 = (-3000, 0, -1500, 1500)      # Centro esquerdo
QUADRANT_7 = (0, 3000, -1500, 1500)       # Centro direito
QUADRANT_8 = (3000, 6000, -1500, 1500)    # Meio direito

QUADRANT_9 = (-6000, -3000, -4500, -1500) # Inferior esquerdo
QUADRANT_10 = (-3000, 0, -4500, -1500)    # Inferior meio-esquerdo
QUADRANT_11 = (0, 3000, -4500, -1500)     # Inferior meio-direito
QUADRANT_12 = (3000, 6000, -4500, -1500)  # Inferior direito

# Lista de todos os quadrantes para facilitar iteração
ALL_QUADRANTS = [
    QUADRANT_1, QUADRANT_2, QUADRANT_3, QUADRANT_4,
    QUADRANT_5, QUADRANT_6, QUADRANT_7, QUADRANT_8,
    QUADRANT_9, QUADRANT_10, QUADRANT_11, QUADRANT_12
]