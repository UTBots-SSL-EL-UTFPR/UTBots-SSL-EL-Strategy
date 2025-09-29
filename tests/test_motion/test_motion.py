import time
import numpy as np
import math
from typing import List
from communication.sender.command_builder import CommandBuilder
from communication.sender.command_sender_sim import CommandSenderSim
from Behaviour_tree.core.field_state import FieldState
from communication.receiver.vision_receiver import VisionReceiver
from communication.parsers.vision_parser import VisionParser



from dataclasses import dataclass

@dataclass
class Pose2D:
    x: float
    y: float
    theta: float  # rad

'''
{w} = referencial da roda
{b} = referencial do robô
{s} = referencial do mundo
'''

toleranciaPonto = 0.03
toleranciaAngulo = 0.5
THETA_OFFSET = math.pi
THETA_SIGN   = +1.0
VMAX = 1
WMAX = 2.5

SCALE = 1
K_POS = 1.2
K_ANG = 0.3

KD_POS = 0.25
KD_ANG = 0.3


def normalize_angle_to_pi(a: float) -> float:
    return (a + math.pi) % (2*math.pi) - math.pi

def compute_world_velocity(
    current,                    # Pose2D(x,y,theta) atual em {s}
    goal,                       # Pose2D(x,y,theta) alvo em {s}
    mode,  # 3 opções diferentes de movimento "maintain_orientation" "precision_movement" "rotation_only"
    
    # ganhos e limites
    k_pos: float = 0.7,         # 1/s ganho linear
    k_ang: float = 0.4,         # 1/s ganho angular (para face_target e etapa 2)
    vmax: float = 1,          # m/s saturação linear
    wmax: float = 2.5,          # rad/s saturação angular

    kd_ang: float = 0.2,
    
    # zonas e tolerâncias, isso é ajutavel e pode ate ser tirado
    slow_radius: float = 0.02,   # m começa a frear ao se aproximar
    pos_tol: float = 0.03,      # m tolerância de posição (chegada de posição)
    ang_tol: float = math.radians(0.5),  # rad tolerância angular (chegada de orientação)

    # deadbands, ajustavel tmb
    v_min: float = 0.20,        # [m/s] piso de velocidade (vencer atrito)
    yaw_deadband: float = math.radians(1.0),  # [rad] ignora correções muito pequenas
):
    """
    Retorna (vx_s, vy_s, w) em {s} seguindo uma das 3 opcoes:
      - maintain_orientation: translada ignorando orientação (w = 0).
      - face_target: olha para a direção do objetivo o tempo todo.
      - goal_orientation: olha para a orientação desejada.
    """

    # erro de posicao para o controle P
    dx = goal.x - current.x
    dy = goal.y - current.y
    dist = math.hypot(dx, dy)

            # Ganhos derivativos (ajuste aqui; mantive fora da assinatura)
    kd_pos = KD_POS   # (adimensional) termo D translacional
    kd_ang = KD_ANG   # (adimensional) termo D angular

    # ================= ERROS EM METROS (x,y) E RAD (theta) =================
    ex = (goal.x - current.x) / SCALE   # m
    ey = (goal.y - current.y) / SCALE   # m
    dist = math.hypot(ex, ey)           # m

    # ================= PD TRANSLACIONAL (em METROS) =================
    # dt translacional
    if mode == "precision_movement":

        now_lin = time.monotonic()
        st_lin = _trans_state
        if st_lin["prev_time"] is None:
            dt_lin = 0.02  # ~50 Hz inicial
        else:
            dt_lin = max(1e-6, now_lin - st_lin["prev_time"])
        st_lin["prev_time"] = now_lin

        if dist < pos_tol:
            vx_s = 0.0
            vy_s = 0.0
            # sincroniza estado para evitar pico ao sair da tolerância
            st_lin["prev_ex"] = ex
            st_lin["prev_ey"] = ey
        else:
            # derivada do erro (m/s)
            d_ex = (ex - st_lin["prev_ex"]) / dt_lin
            d_ey = (ey - st_lin["prev_ey"]) / dt_lin
            st_lin["prev_ex"] = ex
            st_lin["prev_ey"] = ey

            

            # P + D translacional (m/s)
            vx_s = k_pos * ex + kd_pos * d_ex
            vy_s = k_pos * ey + kd_pos * d_ey

            """# rampa perto do último ponto (se aplicável) — usa dist em m
            if isLastMovement and slow_radius > 1e-6 and dist < slow_radius:
                scale = dist / slow_radius
                vx_s *= scale
                vy_s *= scale"""

            # saturação e piso (m/s)
            v = math.hypot(vx_s, vy_s)
            if v > vmax:
                s = vmax / v
                vx_s *= s
                vy_s *= s
                v = vmax
            if 0.0 < v < v_min:
                s = v_min / v
                vx_s *= s
                vy_s *= s
    elif mode == "maintain_orientation":
        if dist < pos_tol:
            vx_s = 0.0
            vy_s = 0.0
        else:
            # controle proporcional em {s}
            vx_s = k_pos * dx
            vy_s = k_pos * dy

            """# rampa suave (linear) perto do alvo. para freiar o robo linearmente quando se chega perto do objetivo. Da pra tirar isso aqui tranquilamente tmb
            # ou fazer ele so atuar quando for o ultimo movimento msm.
            if slow_radius > 1e-6 and dist < slow_radius:
                scale = dist / slow_radius
                vx_s *= scale
                vy_s *= scale"""

            # saturação e piso, ajustavel tmb, eh so pra garantir uma velocidade minima e maxima do robo
            v = math.hypot(vx_s, vy_s)
            if v > vmax:
                vx_s *= vmax / v
                vy_s *= vmax / v
                v = vmax
            if 0.0 < v < v_min:
                vx_s *= v_min / v
                vy_s *= v_min / v

    else:
        vx_s = 0.0
        vy_s = 0.0

    # ================= PD ANGULAR (em RAD) =================
    w = 0.0
    theta_meas = THETA_SIGN * (current.theta + THETA_OFFSET)

    # dt angular
    now_yaw = time.monotonic()
    st_yaw = _yaw_state
    if st_yaw["prev_time"] is None:
        dt_yaw = 0.02
    else:
        dt_yaw = max(1e-6, now_yaw - st_yaw["prev_time"])
    st_yaw["prev_time"] = now_yaw

    if mode == "maintain_orientation":
        w = 0.0
        st_yaw["prev_err"] = 0.0

    elif (mode == "precision_movement" and dist <= 0.2):
        ang_err = normalize_angle_to_pi(goal.theta - theta_meas)

        if abs(ang_err) < yaw_deadband:
            w = 0.0
            st_yaw["prev_err"] = ang_err
        else:
            d_ang_err = (ang_err - st_yaw["prev_err"]) / dt_yaw  # rad/s
            st_yaw["prev_err"] = ang_err

            w = k_ang * ang_err + kd_ang * d_ang_err
            w = max(-wmax, min(wmax, w))
    else:
        ang_err = normalize_angle_to_pi(goal.theta - theta_meas)

        if abs(ang_err) < yaw_deadband:
            w = 0.0
            st_yaw["prev_err"] = ang_err
        else:
            d_ang_err = (ang_err - st_yaw["prev_err"]) / dt_yaw  # rad/s
            st_yaw["prev_err"] = ang_err

            w = k_ang * ang_err + kd_ang * d_ang_err
            w = max(-wmax, min(wmax, w))

    # ================= CONDIÇÃO DE CHEGADA GLOBAL =================
    if dist < pos_tol:
        if mode == "face_target":
            theta_des = math.atan2(ey, ex) if dist > 1e-6 else goal.theta
            ang_err = normalize_angle_to_pi(theta_des - theta_meas)
        elif mode == "precision_movement" or mode == "rotation_only":
            ang_err = normalize_angle_to_pi(goal.theta - theta_meas)
        else:
            ang_err = 0.0

        if abs(ang_err) < ang_tol:
            vx_s = 0.0
            vy_s = 0.0
            w = 0.0

    return vx_s, vy_s, w

def motorVel (q, phi):
    h = np.zeros((nrodas, 3))
    for i in range(nrodas):
        Bi = wheels_angles[i]   # Ângulo entre {w} e {b}
        gammai = gamma[i]
        hi = np.array([robot_radius,
                       np.cos(Bi+phi+gammai),
                       np.sin(Bi+phi+gammai)])
        hi /= (wheel_radius*np.cos(gammai))  # Operações compactadas
        h[i][0] = hi[0]
        h[i][1] = hi[1]
        h[i][2] = hi[2]
    u = h @ q
    return u

def saturate(u, umax):
    return np.clip(u, -umax, umax)



def get_pose_from_receiver_multicam(receiver,
                                    team: str,
                                    robot_id: int,
                                    timeout: float = 0.03):
    """
    isso aqui é so improvisado pra rodar aqui dentro msm, ta quase identico ao test vision receiver q o wesley fez
    """

    # Estado persistente entre chamadas (igual ao test_vision_receiver)
    if not hasattr(get_pose_from_receiver_multicam, "_parser"):
        get_pose_from_receiver_multicam._parser = VisionParser()
    if not hasattr(get_pose_from_receiver_multicam, "_field"):
        get_pose_from_receiver_multicam._field = FieldState()
    if not hasattr(get_pose_from_receiver_multicam, "_last_processed_raw"):
        get_pose_from_receiver_multicam._last_processed_raw = None

    parser = get_pose_from_receiver_multicam._parser
    field  = get_pose_from_receiver_multicam._field
    last_processed_raw = get_pose_from_receiver_multicam._last_processed_raw

    received_cameras = set()
    start_time = time.time()

    # >>> Igual ao seu test_vision_receiver: drena pacotes novos e agrega por câmera
    while time.time() - start_time < timeout:
        raw = receiver.get_latest_raw()
        if raw is not None and raw != last_processed_raw:
            last_processed_raw = raw
            parsed = parser.parse_to_dict(raw)  # usa dict, como no teste
            det = parsed.get("detection", {})
            cam_id = det.get("camera_id")
            if cam_id is not None and cam_id not in received_cameras:
                field.update_from_packet(parsed)
                received_cameras.add(cam_id)

    # guarda o último processado para a próxima chamada
    get_pose_from_receiver_multicam._last_processed_raw = last_processed_raw

    # Extrai do FieldState (mesma fonte consolidada do seu teste)
    state = field.get_state()
    bots = state["robots_blue"] if team.lower() == "blue" else state["robots_yellow"]
    bot = bots.get(robot_id)
    if not bot:
        return None

    x = bot.get("x")
    y = bot.get("y")
    phi = bot.get("orientation")
    if x is None or y is None or phi is None:
        return None

    # mm -> m, rad já vem em rad
    return (x/1000.0, y/1000.0, float(phi))


if __name__ == "__main__":

    #tudo aqui é so pra testar de forma isolada msm

    _yaw_state = {
                "prev_err": 0.0,
                "prev_time": None,
            }
    
    _trans_state = {
                "prev_ex": 0.0,
                "prev_ey": 0.0,
                "prev_time": None,
            }



    #geometria do robo ------------------------------------------------------------------------------------------------
    wheels_angles = [math.radians(-30), 
                 math.radians(45),
                 math.radians(135),
                 math.radians(-150)]
    gamma = [0, 0, 0, 0]
    wheel_radius = 0.027
    robot_radius = 0.09
    nrodas = 4

    # Inicializa os componentes pra visao------------------------------------------------------------------------
    interface_ip_vision="0.0.0.0"
    interface_ip_referee="172.17.0.1"
    receiver = VisionReceiver()
    parser   = VisionParser()
    field = FieldState()
    last_processed_raw = None

    #inicializa os builders------------------------------------------------------------------------------------------
    builder = CommandBuilder()
    sender = CommandSenderSim()

    #destino ---------------------------------------------------------------------------------------------------------
    xg = 0
    yg = 0
    theta_g = math.radians(90)

    #loop de controle---------------------------------------------------------------------------------------------------
    arrived_count = 0
    need_hits = 1  # ~200 ms em 60 Hz
    start = time.time()
    # ---- Controle & logs ----
    segundoPonto = False

    MODE = "precision_movement"  # "maintain_orientation" | "rotation_only" | "precision_movement"
    phi_prev = None                # para derivar yaw
    u_prev = np.zeros((4,1))       # opcional: manter último comando
    k_d = 0.2                      # ganho derivativo do yaw (0.15–0.35)
    wmax_global = 2.5              # saturação final de w
    t_prev = time.time()           # base para dt estável
    last_log = 0.0                 # throttle de prints

    """builder.replace_ball(x = 0.75, y = -1.3, vx = 0, vy = 0)
    packet_bytes = builder.build()
    sender.send(packet_bytes)"""

    count = 0


    builder.command_robots(
        id = 0, kick_x=3
    )
    sender.send(builder.build())
        


    


