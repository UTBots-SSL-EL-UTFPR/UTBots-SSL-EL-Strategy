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

toleranciaPonto = 0.1
toleranciaAngulo = 10
THETA_OFFSET = math.pi
THETA_SIGN   = +1.0


def normalize_angle_to_pi(a: float) -> float:
    return (a + math.pi) % (2*math.pi) - math.pi

def compute_world_velocity(
    current,                    # Pose2D(x,y,theta) atual em {s}
    goal,                       # Pose2D(x,y,theta) alvo em {s}
    mode: str = "maintain_orientation",  # 3 opções diferentes de movimento q eu fiz pra testar "maintain_orientation" | "face_target" | "goal_orientation"
    
    # ganhos e limites
    k_pos: float = 1.4,         # 1/s ganho linear
    k_ang: float = 0.9,         # 1/s ganho angular (para face_target e etapa 2)
    vmax: float = 1.5,          # m/s saturação linear
    wmax: float = 2.5,          # rad/s saturação angular
    
    # zonas e tolerâncias, isso é ajutavel e pode ate ser tirado
    slow_radius: float = 0.02,   # m começa a frear ao se aproximar
    pos_tol: float = 0.03,      # m tolerância de posição (chegada de posição)
    ang_tol: float = math.radians(2.0),  # rad tolerância angular (chegada de orientação)

    # deadbands, ajustavel tmb
    v_min: float = 0.10,        # [m/s] piso de velocidade (vencer atrito)
    yaw_deadband: float = math.radians(3.0),  # [rad] ignora correções muito pequenas
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

    # ================= VELOCIDADES LINEARES (em {s}) =================
    if dist < pos_tol:
        vx_s = 0.0
        vy_s = 0.0
    else:
        # controle proporcional em {s}
        vx_s = k_pos * dx
        vy_s = k_pos * dy

        # rampa suave (linear) perto do alvo. para freiar o robo linearmente quando se chega perto do objetivo. Da pra tirar isso aqui tranquilamente tmb
        # ou fazer ele so atuar quando for o ultimo movimento msm.
        if slow_radius > 1e-6 and dist < slow_radius:
            scale = dist / slow_radius
            vx_s *= scale
            vy_s *= scale

        # saturação e piso, ajustavel tmb, eh so pra garantir uma velocidade minima e maxima do robo
        v = math.hypot(vx_s, vy_s)
        if v > vmax:
            vx_s *= vmax / v
            vy_s *= vmax / v
            v = vmax
        if 0.0 < v < v_min:
            vx_s *= v_min / v
            vy_s *= v_min / v

    # ================= CONTROLE DE ORIENTAÇÃO =================
    w = 0.0
    theta_meas = THETA_SIGN * (current.theta + THETA_OFFSET)

    if mode == "maintain_orientation":
        # nunca gira; só translada.
        w = 0.0

    elif mode == "face_target":
        # olha para na direcao do ponto desejado o tempo todo (mesmo durante a translação).
        theta_des = math.atan2(dy, dx) if dist > 1e-6 else goal.theta
        ang_err = normalize_angle_to_pi(theta_des - theta_meas)

        # controle P no yaw agr
        if abs(ang_err) >= yaw_deadband:
            w = k_ang * ang_err
            w = max(-wmax, min(w, wmax))
        else:
            w = 0.0

    elif mode == "goal_orientation":
        # olha para um angulo passado q nao necessariamente é na direcao do ponto desejado
        
        ang_err = normalize_angle_to_pi(goal.theta - theta_meas)

        if abs(ang_err) >= yaw_deadband:
            w = k_ang * ang_err * 3
            w = max(-wmax, min(w, wmax))
        else:
            w = 0.0
    else:
        raise ValueError(f"mode inválido: {mode!r}. Use 'maintain_orientation', 'face_target' ou 'goal_orientation'.")

    # ================= CONDIÇÃO DE CHEGADA GLOBAL =================
    if dist < pos_tol:
        # para decidir se zera tudo: depende do modo
        if mode == "face_target":
            theta_des = math.atan2(dy, dx) if dist > 1e-6 else goal.theta
            ang_err = normalize_angle_to_pi(theta_des - theta_meas)
        elif mode == "goal_orientation":
            ang_err = normalize_angle_to_pi(goal.theta - theta_meas)
        else:
            ang_err = 0.0  # maintain_orientation não exige yaw especifico, ent fds

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
    builder = CommandBuilder(team_color="blue")
    sender = CommandSenderSim()

    #destino ---------------------------------------------------------------------------------------------------------
    xg = 0.75
    yg = -1.3
    theta_g = math.radians(90)

    #loop de controle---------------------------------------------------------------------------------------------------
    arrived_count = 0
    need_hits = 12  # ~200 ms em 60 Hz
    start = time.time()
    # ---- Controle & logs ----
    segundoPonto = False

    MODE = "goal_orientation"  # "maintain_orientation" | "face_target" | "goal_orientation"
    phi_prev = None                # para derivar yaw
    u_prev = np.zeros((4,1))       # opcional: manter último comando
    k_d = 0.2                      # ganho derivativo do yaw (0.15–0.35)
    wmax_global = 2.5              # saturação final de w
    t_prev = time.time()           # base para dt estável
    last_log = 0.0                 # throttle de prints

    """builder.replace_ball(x = 0.75, y = -1.3, vx = 0, vy = 0)
    packet_bytes = builder.build()
    sender.send(packet_bytes)"""

    while True:
        now = time.time()
        dt = max(1e-3, now - t_prev)
        t_prev = now

        # lê pose UMA vez por ciclo
        pose = get_pose_from_receiver_multicam(receiver, "blue", 0, timeout=0.03)

        # valores default
        vx_s = vy_s = w = 0.0
        phi = phi_prev if phi_prev is not None else 0.0

        if pose is not None:
            x, y, phi = pose
            vx_s, vy_s, w = compute_world_velocity(
                current=Pose2D(x, y, phi),
                goal=Pose2D(xg, yg, theta_g),
                mode=MODE
            )

            # --- PD no yaw (so ideia por enquanto) ---
            yaw_rate = 0.0
            if phi_prev is not None:
                dphi = ((phi - phi_prev + math.pi) % (2*math.pi)) - math.pi
                yaw_rate = dphi / dt

            apply_D = (MODE == "face_target")
            # no goal_orientation: só aplica D na etapa 2 (quando já está no ponto)
            if MODE == "goal_orientation":
                dx_tmp, dy_tmp = (xg - x), (yg - y)
                dist_tmp = math.hypot(dx_tmp, dy_tmp)
                apply_D = apply_D or (dist_tmp < toleranciaPonto)

            if apply_D:
                w = w - k_d * yaw_rate
            # saturação angular final
            w = max(-wmax_global, min(w, wmax_global))

            # verificação de chegada (debounce)
            dx, dy = (xg - x), (yg - y)
            dist = math.hypot(dx, dy)
            ang_err = ((theta_g - phi + math.pi) % (2*math.pi)) - math.pi
            if (MODE == "maintain_orientation" and dist < toleranciaPonto) or \
            (MODE != "maintain_orientation" and dist < toleranciaPonto and abs(ang_err) < math.radians(toleranciaAngulo)):
                arrived_count += 1
            else:
                arrived_count = 0

        # log com throttle (não interfere no cálculo)
        if now - last_log > 0.5:
            print("pose:", pose, "arrived_count:", arrived_count)
            last_log = now

        # monta q e cinemática
        q = np.array([[w], [vx_s], [vy_s]], dtype=float)
        u = motorVel(q, phi)
        u = np.clip(u, -120.0, 120.0)

        builder.command_robots(
            id=0, wheelsspeed=True,
            wheel1=-u[0].item(), wheel2=-u[1].item(),
            wheel3=-u[2].item(), wheel4=-u[3].item()
        )
        sender.send(builder.build())

        u_prev = u

        if arrived_count >= need_hits:
            builder.command_robots(id=0, wheelsspeed=True, wheel1=0.0, wheel2=0.0, wheel3=0.0, wheel4=0.0)
            sender.send(builder.build())
            break

        phi_prev = phi
        time.sleep(max(0.0, 1/60 - (time.time() - now)))

    builder.command_robots(
            id=0, kick_x=4.0
        )
    start_time = time.time()

    while time.time() - start_time < 1.0:
        packet_bytes = builder.build()
        sender.send(packet_bytes)
        time.sleep(0.016)  # ~60 pacotes por segundo

    


