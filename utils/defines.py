# defines.py
import math

# ===================================================#
# ==== CONSTANTES DE LÓGICA DE JOGO (Escala 'MM') ===#
# ===================================================#
# Flag global: True se o time defende o gol da direita (campo invertido)
FIELD_INVERTED_SIDE = False  # Altere para True se seu time defende o lado direito
LOGIC_ROBOT_RADIUS = 90
LOGIC_BALL_RADIUS = 15
BALL_POSSESSION_DISTANCE = LOGIC_ROBOT_RADIUS + LOGIC_BALL_RADIUS + 250
BALL_LOSS_DISTANCE = LOGIC_ROBOT_RADIUS + LOGIC_BALL_RADIUS + 350

MIN_PASS_DISTANCE = 1000
MAX_SHOOT_DISTANCE = 1500
DISTANCE_PRESS_OPPONENT = 400
INFLUENCE_RADIUS = 500
FREE_DISTANCE = 1  # (Do seu arquivo original)

# ===================================================#
# ==== CONSTANTES DE UNIDADE E ÍNDICES            ====#
# ===================================================#
SCALE = 1000.0
LOWER = 0
UPPER = 1

# ===================================================#
# ==== CONSTANTES DE CINEMÁTICA (Física / Metros) ===#
# ===================================================#
KINEMATIC_THETA_SIGN = +1.0
KINEMATIC_THETA_OFFSET = math.pi
KINEMATIC_N_RODAS = 4
KINEMATIC_WHEELS_ANGLES = [
    math.radians(-30),
    math.radians(45),
    math.radians(135),
    math.radians(-150),
]
KINEMATIC_GAMMA = [0, 0, 0, 0]
KINEMATIC_ROBOT_RADIUS = 0.09
KINEMATIC_WHEEL_RADIUS = 0.027
KINEMATIC_MAX_WHEEL_SPEED = 120.0

# ===================================================#
# ==== GANHOS DE CONTROLE GLOBAIS                 ====#
# ===================================================#
# (Valores que estavam no topo do seu bob.py)
GLOBAL_VMAX = 1.0
GLOBAL_WMAX = 2.5
GLOBAL_K_POS = 1.2
GLOBAL_K_ANG = 0.3
GLOBAL_KD_POS = 0.25
GLOBAL_KD_ANG = 0.3

# ===================================================#
# ==== PARÂMETROS DA FUNÇÃO (Controle / Metros)   ====#
# ===================================================#

CONTROL_K_POS = 0.7  # 1/s ganho linear
CONTROL_K_ANG = 0.4  # 1/s ganho angular
CONTROL_KD_ANG_FUNC = 0.2  # Ganho derivativo angular específico da função
CONTROL_V_MAX = 0.5  # m/s saturação linear
CONTROL_W_MAX = 2.5  # rad/s saturação angular
CONTROL_POS_TOL = 0.03  # m tolerância de posição
CONTROL_ANG_TOL = math.radians(0.04)  # rad tolerância angular
CONTROL_V_MIN = 0.20  # [m/s] piso de velocidade (vencer atrito)
CONTROL_YAW_DEADBAND = math.radians(1.0)  # [rad] ignora correções pequenas
CONTROL_DEFAULT_DT = 0.02  # 50 Hz (para dt inicial)
CONTROL_DT_EPSILON = 1e-6  # Valor mínimo para dt
CONTROL_ROTATION_THRESHOLD_DIST = 0.2  # metros (dist p/ focar só rotação)

# ~50 Hz inicial (CONSIDERANDO Q VAMOS MANTER COM 50HZ MSM, SE MUDAR ISSO, TEM Q MUDAR AQUI TMB)
DELTA_T = 0.02
