# bob.py

import math
import time

import numpy as np

from Behaviour_tree.core.event_callbacks import BlackboardKeys
from utils import utilsp
from utils.pose2D import Pose2D

from ..core.blackboard import Blackboard_Manager
from ..core.World_State import TeamID
from .bob_config import Bob_Config
from .bob_state import Bob_State
from .foes import FoesState

positions = BlackboardKeys.Values.Positions

# from Behaviour_tree.helpers.positioning_helper import visibilidade_gol TODO @DANILO sla oq q c ta importando aq, mas c tem q trazer a classe toda
from communication.sender.command_builder import CommandBuilder
from communication.sender.command_sender_sim import CommandSenderSim

# --------------------------------------------DEFINES--------------------------------------------#
LOWER = 0
UPPER = 1
THETA_SIGN = +1.0
THETA_OFFSET = math.pi
N_RODAS = 4
WHEELS_ANGLES = [
    math.radians(-30),
    math.radians(45),
    math.radians(135),
    math.radians(-150),
]
GAMMA = [0, 0, 0, 0]
ROBOT_RADIUS = 0.09
WHEEL_RADIUS = 0.027
FREE_DISTANCE = 1

VMAX = 1
WMAX = 2.5

SCALE = 1000.0
K_POS = 1.2
K_ANG = 0.3

KD_POS = 0.25
KD_ANG = 0.3


class Bob:

    def __init__(self, robot_id: TeamID):
        self._bb = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.state: Bob_State = Bob_State(robot_id)
        self._has_ball = False
        self.cmd_builder = CommandBuilder()
        self.cmd_sender = CommandSenderSim()
        self.cmd: bytes | None = None
        self._trans_state = {
            "prev_ex": 0.0,
            "prev_ey": 0.0,
            "prev_time": None,
        }
        self._yaw_state = {
            "prev_err": 0.0,
            "prev_time": None,
        }

    def update(self):
        if self.state:
            self._bb.set(
                f"{self.robot_id.name}{BlackboardKeys.Flags.Navigation.TARGET_REACHED}",
                False,
            )
            self.state.update()

    def adicionar_ponto_trajetoria(self, target: Pose2D):
        self.state.path.append(target)

    def set_path(self, path: list[Pose2D]):
        self.state.path = path
        self.state.path_index = 0

    def set_new_target(self, target_position: Pose2D):
        self.state.path.clear()
        self.state.path_index = 0
        self.adicionar_ponto_trajetoria(target_position)

    def precision_movement(self):  # usa o movimento de precisao
        if self.state is None:
            return
        """
        Move o bob de sua pose2d atual ate outra pose2d com precisao de posicao e angulo
        """
        vx_s, vy_s, w = self.compute_world_velocity(
            self.state.position, self.state.target_position, mode="precision_movement"
        )

        q = np.array([[w], [vx_s], [vy_s]], dtype=float)

        # velocidade individual de cada roda
        u = self.motorVel(q, self.state.position.theta)
        u = np.clip(u, -120.0, 120.0)

        # envia um pacote
        self.cmd_builder.command_robots(
            id=self.robot_id.value,
            wheelsspeed=True,
            wheel1=-u[0].item(),
            wheel2=-u[1].item(),
            wheel3=-u[2].item(),
            wheel4=-u[3].item(),
        )
        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)

    def fast_movement(self):
        """
        Move o bob de sua pose2d atual ate outra pose2d com velocidade sem se importar com o angulo
        """
        if self.state.target_position is None:
            return
        vx_s, vy_s, w = self.compute_world_velocity(
            self.state.position, self.state.target_position, mode="maintain_orientation"
        )
        q = np.array([[w], [vx_s], [vy_s]], dtype=float)

        # velocidade individual de cada roda
        u = self.motorVel(q, self.state.position.theta)
        u = np.clip(u, -120.0, 120.0)

        # envia um pacote
        self.cmd_builder.command_robots(
            id=self.robot_id.value,
            wheelsspeed=True,
            wheel1=-u[0].item(),
            wheel2=-u[1].item(),
            wheel3=-u[2].item(),
            wheel4=-u[3].item(),
        )
        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)

    def rotate(self):
        if self.state is None:
            return
        """
        Apenas rotaciona o bob de sua pose2d atual ate outra pose2d 
        """
        vx_s, vy_s, w = self.compute_world_velocity(
            self.state.position, self.state.target_position, mode="rotation_only"
        )
        q = np.array([[w], [vx_s], [vy_s]], dtype=float)

        # velocidade individual de cada roda
        u = self.motorVel(q, self.state.position.theta)
        u = np.clip(u, -120.0, 120.0)

        # envia um pacote
        self.cmd_builder.command_robots(
            id=self.robot_id.value,
            wheelsspeed=True,
            wheel1=-u[0].item(),
            wheel2=-u[1].item(),
            wheel3=-u[2].item(),
            wheel4=-u[3].item(),
        )
        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)

    def stop(self):
        """Interrompe qualquer movimento do robô."""
        self.state.path.clear()
        self.set_new_target(self.state.position)
        self.state.current_command = "Parado"

    def kick_ball(self, ballSpeed: float = 3.0) -> bool:
        """
        a bola tem q estar encostada no chutador na frente do robo, o chutador
        no simulador nao se projeta pra frente, ele so pisca em vermelho como
        indicativo visual de q foi acionado.
        """

        if self.state is None:
            return False

        self.cmd_builder.command_robots(id=self.robot_id.value, kick_x=ballSpeed)

        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)
        return True

    def compute_world_velocity(
        self,
        current,  # Pose2D(x,y,theta) atual em {s}
        goal,  # Pose2D(x,y,theta) alvo em {s}
        mode,  # 3 opções diferentes de movimento "maintain_orientation" "precision_movement" "rotation_only"
        # ganhos e limites
        k_pos: float = 0.7,  # 1/s ganho linear
        k_ang: float = 0.4,  # 1/s ganho angular (para face_target e etapa 2)
        vmax: float = 0.5,  # m/s saturação linear
        wmax: float = 2.5,  # rad/s saturação angular
        kd_ang: float = 0.2,
        # zonas e tolerâncias, eh ajutavel
        pos_tol: float = 0.03,  # m tolerância de posição (chegada de posição)
        ang_tol: float = math.radians(
            0.5
        ),  # rad tolerância angular (chegada de orientação)
        # deadbands, ajustavel tmb
        v_min: float = 0.20,  # [m/s] piso de velocidade (vencer atrito)
        yaw_deadband: float = math.radians(
            1.0
        ),  # [rad] ignora correções muito pequenas
    ):
        """
        Retorna (vx_s, vy_s, w) em {s} seguindo uma das 3 opcoes:
        - maintain_orientation: translada ignorando orientação (w = 0).
        - rotation_only: so rotaciona.
        - precision_movement: translada e rotaciona com precisao.
        """

        # erro de posicao para o controle P
        dx = goal.x - current.x
        dy = goal.y - current.y
        dist = math.hypot(dx, dy)

        # Ganhos derivativos
        kd_pos = KD_POS
        kd_ang = KD_ANG

        # ================= ERROS EM METROS (x,y) E RAD (theta) =================
        ex = (goal.x - current.x) / SCALE  # m
        ey = (goal.y - current.y) / SCALE  # m
        dist = math.hypot(ex, ey)  # m

        # ================= PD TRANSLACIONAL (em METROS) =================
        # dt translacional
        if mode == "precision_movement":

            now_lin = time.monotonic()
            st_lin = self._trans_state
            if st_lin["prev_time"] is None:
                dt_lin = 0.02  # ~50 Hz inicial (CONSIDERANDO Q VAMOS MANTER COM 50HZ MSM, SE MUDAR ISSO, TEM Q MUDAR AQUI TMB)
            else:
                dt_lin = max(1e-6, now_lin - st_lin["prev_time"])
            st_lin["prev_time"] = now_lin

            if dist < pos_tol:
                vx_s = 0.0
                vy_s = 0.0
                # sincroniza estado para evitar pico ao sair da tolerancia
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
        st_yaw = self._yaw_state
        if st_yaw["prev_time"] is None:
            dt_yaw = 0.02
        else:
            dt_yaw = max(1e-6, now_yaw - st_yaw["prev_time"])
        st_yaw["prev_time"] = now_yaw

        if mode == "maintain_orientation":
            w = 0.0
            st_yaw["prev_err"] = 0.0

        elif mode == "precision_movement" and dist <= 0.2:
            ang_err = Pose2D.normalize_angle_to_pi(goal.theta - theta_meas)

            if abs(ang_err) < yaw_deadband:
                w = 0.0
                st_yaw["prev_err"] = ang_err
            else:
                d_ang_err = (ang_err - st_yaw["prev_err"]) / dt_yaw  # rad/s
                st_yaw["prev_err"] = ang_err

                w = k_ang * ang_err + kd_ang * d_ang_err
                w = max(-wmax, min(wmax, w))
        else:
            ang_err = Pose2D.normalize_angle_to_pi(goal.theta - theta_meas)

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
            if mode == "precision_movement" or mode == "rotation_only":
                ang_err = Pose2D.normalize_angle_to_pi(goal.theta - theta_meas)
            else:
                ang_err = 0.0

            if abs(ang_err) < ang_tol:
                vx_s = 0.0
                vy_s = 0.0
                w = 0.0

        return vx_s, vy_s, w

    def motorVel(self, q, phi):
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
            Bi = WHEELS_ANGLES[i]  # Ângulo entre {w} e {b}
            gammai = GAMMA[i]
            hi = np.array(
                [ROBOT_RADIUS, np.cos(Bi + phi + gammai), np.sin(Bi + phi + gammai)]
            )
            hi /= WHEEL_RADIUS * np.cos(gammai)  # Operações compactadas
            h[i][0] = hi[0]
            h[i][1] = hi[1]
            h[i][2] = hi[2]
        u = h @ q
        u = np.clip(u, -120.0, 120.0)

        return u

    # ===================================================#
    # ==== metodos auxiliares para os metodos do BOB ====#
    def shoot_to_goal(self, goal_position: Pose2D) -> bool:
        if self.state is None:
            return False
        if not self._has_ball:
            return False
        my_pos = self.state.get_position()
        dx = goal_position.x - my_pos.x
        dy = goal_position.y - my_pos.y
        self.state.target_theta = math.atan2(dy, dx)
        self.rotate()
        return self.kick_ball()

    def pass_to_teammate(self, teammate_pos: Pose2D) -> bool:
        if self.state is None:
            return False
        my_pos = self.state.get_position()
        dx = teammate_pos.x - my_pos.x
        dy = teammate_pos.y - my_pos.y
        self.state.target_theta = math.atan2(dy, dx)
        self.rotate()
        return self.kick_ball()
