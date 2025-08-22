# bob.py

from .bob_state import Bob_State
from .bob_config import Bob_Config
from utils import utilsp
from .foes import Foes_State
import math
import numpy as np
from math import sqrt
from utils.pose2D import Pose2D
from ..core.World_State import RobotID
from ..core.blackboard import Blackboard_Manager
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions

from communication.sender.command_builder import CommandBuilder
from communication.sender.command_sender_sim import CommandSenderSim
#--------------------------------------------DEFINES--------------------------------------------#
LOWER = 0
UPPER = 1
THETA_SIGN = +1.0
THETA_OFFSET = math.pi
N_RODAS = 4
WHEELS_ANGLES = [math.radians(-30), 
                 math.radians(45),
                 math.radians(135),
                 math.radians(-150)]
GAMMA = [0, 0, 0, 0]
ROBOT_RADIUS = 0.09
WHEEL_RADIUS = 0.027


class Bob:

    def __init__(self, robot_id: RobotID):
        self._bb = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.config = Bob_Config(robot_id)
        self.state: Bob_State | None = Bob_State(robot_id)
        self._has_ball = False
        self.foes: list[Foes_State] #TODO
        self.cmd_builder = CommandBuilder()
        self.cmd_sender = CommandSenderSim()
        self.cmd : bytes | None = None

    def move(self, vel_x: float, vel_y: float) -> bool:
        return True
    
    def update(self):
        if(self.state):
            self._bb.set(f"{self.robot_id.name}{navigation_flags.target_reached}", False)
            self.state.update()

    def set_movment(self, target: Pose2D):
        if(self.state):
            self.state.target_position = target

    def move_oriented(self):
        if self.state is None:
            return
        """
        Move o bob de sua pose2d atual ate outra pose2d
        """
        vx_s, vy_s, w = self.compute_world_velocity(self.state.position, self.state.target_position)
        q = np.array([[w], [vx_s], [vy_s]], dtype=float)

        #velocidade individual de cada roda
        u = self.motorVel(q, self.state.position.theta)
        u = np.clip(u, -120.0, 120.0)

        #envia um pacote
        self.cmd_builder.command_robots(
            id=self.robot_id.value, wheelsspeed=True,
            wheel1=-u[0].item(), wheel2=-u[1].item(),
            wheel3=-u[2].item(), wheel4=-u[3].item()
        )
        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)

    def kick_ball(self) -> bool:
        #TODO enviar comando para simulação
        return True

    def rotate(self, angle: float) -> bool:
        #TODO ENVIAR COMANDO ROTATE (é melhor controlar com encoders)
        return True
    
    def compute_world_velocity(
        self,
        current,                    # Pose2D(x,y,theta) atual em {s}
        goal,                       # Pose2D(x,y,theta) alvo em {s}
        mode: str = "maintain_orientation",  # 3 opções diferentes de movimento q eu fiz pra testar "maintain_orientation" | "face_target" | "goal_orientation"
        
        # ganhos e limites
        k_pos: float = 1.4,         # 1/s ganho linear
        k_ang: float = 0.9,         # 1/s ganho angular (para face_target e etapa 2)
        vmax: float = 0.5,          # m/s saturação linear
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
            ang_err = Pose2D.normalize_angle_to_pi(theta_des - theta_meas)

            # controle P no yaw agr
            if abs(ang_err) >= yaw_deadband:
                w = k_ang * ang_err
                w = max(-wmax, min(w, wmax))
            else:
                w = 0.0

        elif mode == "goal_orientation":
            # olha para um angulo passado q nao necessariamente é na direcao do ponto desejado
            
            ang_err = Pose2D.normalize_angle_to_pi(goal.theta - theta_meas)

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
                ang_err = Pose2D.normalize_angle_to_pi(theta_des - theta_meas)
            elif mode == "goal_orientation":
                ang_err = Pose2D.normalize_angle_to_pi(goal.theta - theta_meas)
            else:
                ang_err = 0.0  # maintain_orientation não exige yaw especifico, ent fds

            if abs(ang_err) < ang_tol:
                vx_s = 0.0
                vy_s = 0.0
                w = 0.0

        print(int(vx_s), int(vy_s), w)
        return vx_s, vy_s, w

    def motorVel (self, q, phi):

        """
        Aqui é o modelo cinematico da gracia.
        {w} = referencial da roda
        {b} = referencial do robô
        {s} = referencial do mundo

        phi é o angulo atual do robo em relação a {s}

        essa funcao tem q receber um vetor com as velocidades em {s}: 
            q = np.array([[w], [vx_s], [vy_s]], dtype=float)
        com isso, ela monta a matriz de transformação H e resolve:
            u = H @ q
        depois satura em [-u_max, u_max].

        retorna um vetor com as velocidades das rodas

        """

        h = np.zeros((N_RODAS, 3))
        for i in range(N_RODAS):
            Bi = WHEELS_ANGLES[i]   # Ângulo entre {w} e {b}
            gammai = GAMMA[i]
            hi = np.array([ROBOT_RADIUS,
                        np.cos(Bi+phi+gammai),
                        np.sin(Bi+phi+gammai)])
            hi /= (WHEEL_RADIUS*np.cos(gammai))  # Operações compactadas
            h[i][0] = hi[0]
            h[i][1] = hi[1]
            h[i][2] = hi[2]
        u = h @ q
        u = np.clip(u, -120.0, 120.0)

        return u



    #===================================================#
    #==== metodos auxiliares para os metodos do BOB ====#

    @staticmethod
    def is_free(x: float, y: float, obstacules: list[Pose2D], raio: float) -> bool:
        # Verifica se (x,y) está distante o suficiente de cada obstáculo
        for obs in obstacules:
            if sqrt((x - obs.x)**2 + (y - obs.y)**2) < raio * 2.2:
                return False
        return True

    def find_shortest_path(self, start: Pose2D, end: Pose2D, obstacules: list[Pose2D], raio: float):
        from collections import deque
        step = 20  # Resolução da grade (ajuste conforme necessário)
        start_cell = (int(start.x // step), int(start.y // step))
        end_cell = (int(end.x // step), int(end.y // step))

        # BFS tradicional
        queue = deque([start_cell])
        visited = {start_cell: None} 

        while queue:
            current = queue.popleft()
            if current == end_cell:
                # Reconstrói caminho
                path_rev = []
                while current is not None:
                    cx, cy = current
                    path_rev.append(Pose2D(cx*step, cy*step))
                    current = visited[current]
                return list(reversed(path_rev))

            cx, cy = current
            # Movimentos 8-direções (ou 4, se preferir)
            for nx, ny in [
                (cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1),
                (cx+1, cy+1), (cx-1, cy-1), (cx+1, cy-1), (cx-1, cy+1)
            ]:
                if (nx, ny) not in visited:
                    wx, wy = nx*step, ny*step
                    if Bob.is_free(wx, wy, obstacules, raio):
                        visited[(nx, ny)] = current # type: ignore
                        queue.append((nx, ny))

        return [start]  # Caso não encontre caminho
    
    def go_to_ball(self, ball_position: Pose2D) -> bool:
        return self.move(ball_position.x, ball_position.y)
    
    def go_to_point_avoiding_obstacles(self, dest: Pose2D, obstacules: list[Pose2D], raio: float) -> bool:
        if self.state is None:
            return False
        start = self.state.get_position()
        path = self.find_shortest_path(start, dest, obstacules, raio)
        if path and len(path) > 1:
            next_step = path[1]
            return self.move(next_step.x, next_step.y)
        else:
            return self.move(dest.x, dest.y)
        
    def shoot_to_goal(self, goal_position: Pose2D) -> bool:
        if self.state is None:
            return False
        if not self._has_ball:
            return False
        my_pos = self.state.get_position()
        dx = goal_position.x - my_pos.x
        dy = goal_position.y - my_pos.y
        angle_to_goal = math.atan2(dy, dx)
        self.rotate(angle_to_goal)
        return self.kick_ball()
    
    def mark_opponent(self, opponent_pos: Pose2D, own_goal: Pose2D) -> bool:
        # Posição entre oponente e o gol (interceptação simples)
        intercept_x = (opponent_pos.x + own_goal.x) / 2
        intercept_y = (opponent_pos.y + own_goal.y) / 2
        return self.move(intercept_x, intercept_y)
    
    def pass_to_teammate(self, teammate_pos: Pose2D) -> bool:
        if self.state is None:
            return False
        my_pos = self.state.get_position()
        dx = teammate_pos.x - my_pos.x
        dy = teammate_pos.y - my_pos.y
        angle = math.atan2(dy, dx)
        self.rotate(angle)
        return self.kick_ball()

    def dribble_towards(self, target_pos: Pose2D) -> bool:
        if not self._has_ball:
            return False
        return self.move(target_pos.x, target_pos.y)


    def is_visible(self):
        #TODO
        pass


    def valid_range(self, position1:tuple[float, float], position2:tuple[float, float], limit:tuple[float, float]):
        distance = utilsp.get_distance(position1, position2)
        if distance > limit[LOWER]  and distance < limit[UPPER]:
            return True
        return False

    def distance_nearest_foe(self):
        if self.state is None:
            return False
        distances =[]
        for foe in  self.foes:
            distances.append(self.state.position.distance_to(foe.position))
        self.nearest_foe = utilsp.min(distances)