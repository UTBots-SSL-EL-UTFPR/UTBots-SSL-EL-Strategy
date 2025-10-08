# defines.py -> mudar para config

# Flag global: True se o time defende o gol da direita (campo invertido)
FIELD_INVERTED_SIDE = False  # Altere para True se seu time defende o lado direito
ROBOT_RADIUS = int(90)

BALL_RADIUS = 15  # Raio da bola em metros
BALL_POSSESSION_DISTANCE = ROBOT_RADIUS + BALL_RADIUS + 250  # Distância de posse da bola
MIN_PASS_DISTANCE = 1000

BALL_DISTANCE_FOR_SHOOT = 150

MAX_SHOOT_DISTANCE = 1500
DISTANCE_PRESS_OPPONENT = 200
INFLUENCE_RADIUS = 500
