# defines.py -> mudar para config

# Flag global: True se o time defende o gol da direita (campo invertido)
FIELD_INVERTED_SIDE = False  # Altere para True se seu time defende o lado direito
ROBOT_RADIUS = int(90)

BALL_RADIUS = 15  # Raio da bola em metros
BALL_POSSESSION_DISTANCE = (
    ROBOT_RADIUS + BALL_RADIUS + 250
)  # Distância de posse da bola
MIN_PASS_DISTANCE = 1000
BALL_DISTANCE_FOR_KICK = 80   # Distância que o robô deve estar da bola para chutar

MAX_SHOOT_DISTANCE = 2000
DISTANCE_PRESS_OPPONENT = 400
INFLUENCE_RADIUS = 500

# Velocidade lenta usada no estado HALT (m/s)
HALT_SLOW_SPEED = 0.1
