import math
import time
from enum import Enum

import numpy as np

from Behaviour_tree.helpers.motion_helper import MotionHelper
from communication.sender.command_builder import CommandBuilder
from communication.sender.command_sender_sim import CommandSenderSim
from utils import defines
from utils.pose2D import Pose2D

from ..core.blackboard import Blackboard_Manager
from .bob_state import Bob_State


class TeamID(Enum):
    Kamiji = 0
    Argenton = 1
    SabKawa = 2


class Bob:

    def __init__(self, robot_id: TeamID):
        self._bb = Blackboard_Manager.get_instance()
        self.robot_id = robot_id
        self.state: Bob_State = Bob_State()
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

    # ===================================================#
    # ==== GERENCIAMENTO DE ESTADO E TRAJETÓRIA      ====#
    # ===================================================#

    def adicionar_ponto_trajetoria(self, target: Pose2D):
        self.state.path.append(target)

    def set_path(self, path: list[Pose2D]):
        self.state.path = path
        self.state._path_index = 0

    def set_new_target_position(self, target_position: Pose2D):
        self.state.path.clear()
        self.state._path_index = 0
        self.adicionar_ponto_trajetoria(target_position)

    def set_new_target_angle(self, theta: float):
        self.state.target_theta = theta
        new_pos = self.state.position
        new_pos.theta = theta
        self.set_new_target_position(new_pos)

    # ===================================================#
    # ==== COMPORTAMENTOS DE ALTO NÍVEL (AÇÕES)      ====#
    # ===================================================#

    def shoot_to_goal(self, goal_position: Pose2D):
        if self.state is None:
            return False
        if not self._has_ball:
            return False
        my_pos = self.state.position
        dx = goal_position.x - my_pos.x
        dy = goal_position.y - my_pos.y
        self.state.target_theta = math.atan2(dy, dx)
        self.rotate()
        self.kick_ball()

    def pass_to_teammate(self, teammate_pos: Pose2D):
        if self.state is None:
            return False
        my_pos = self.state.position
        dx = teammate_pos.x - my_pos.x
        dy = teammate_pos.y - my_pos.y
        self.state.target_theta = math.atan2(dy, dx)
        self.rotate()
        self.kick_ball()

    # ===================================================#
    # ==== PRIMITIVAS DE MOVIMENTO (COMO SE MOVER)   ====#
    # ===================================================#
    def Move(self):
        if not self.state.target_position:
            return
        if self.state.fast_mov:
            self.fast_movement()
        else:
            self.precision_movement()

    def precision_movement(self):
        self._execute_movement(mode="precision_movement")

    def fast_movement(self):
        """
        Move o bob de sua pose2d atual ate outra pose2d com velocidade sem se importar com o angulo
        """
        self._execute_movement(mode="maintain_orientation")

    def rotate(self):
        """
        Apenas rotaciona o bob de sua pose2d atual ate outra pose2d
        """
        self._execute_movement(mode="rotation_only")

    def kick_ball(self, ballSpeed: float = 3.0):
        """
        a bola tem q estar encostada no chutador na frente do robo, o chutador
        no simulador nao se projeta pra frente, ele so pisca em vermelho como
        indicativo visual de q foi acionado.
        """
        
        self.cmd_builder.command_robots(
            id=self.robot_id.value, kick_x=ballSpeed, kick_z=4
        )

        self.cmd = self.cmd_builder.build()
        self.cmd_sender.send(self.cmd)

    def _execute_movement(self, mode: str):
        """
        Função auxiliar interna para executar qualquer tipo de movimento.

        Ela pega o 'mode', calcula as velocidades do robô,
        converte para velocidades de roda e envia o comando.
        """
        if self.state is None or self.state.target_position is None:
            return

        vx_s, vy_s, w = self.compute_world_velocity(
            self.state.position, self.state.target_position, mode=mode
        )

        q = np.array([[w], [vx_s], [vy_s]], dtype=float)
        u = MotionHelper.motorVel(q, self.state.position.theta)

        u = np.clip(
            u, -defines.KINEMATIC_MAX_WHEEL_SPEED, defines.KINEMATIC_MAX_WHEEL_SPEED
        )

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

        """
        bloco temporário para enviar os comandos para os robos reais tmb
        """

    def compute_world_velocity(self, current: Pose2D, goal: Pose2D | None, mode: str):
        """
        Retorna (vx_s, vy_s, w) em {s}.
        - Para 'precision_movement' e 'maintain_orientation', usa o 'goal' (Pose2D).
        - Para 'rotation_only', usa 'self.state.target_theta' (float).
        """

        # ================= 1. CÁLCULO DE ERROS E ALVO =================

        target_angle_to_use: float = 0.0
        if mode == "rotation_only":

            if self.state.target_theta is None:
                return 0.0, 0.0, 0.0

            target_angle_to_use = self.state.target_theta

            dx, dy, ex, ey, dist = 0.0, 0.0, 0.0, 0.0, 0.0

        else:
            if goal is None:
                return 0.0, 0.0, 0.0

            target_angle_to_use = goal.theta

            dx = goal.x - current.x
            dy = goal.y - current.y
            ex = dx / defines.SCALE
            ey = dy / defines.SCALE
            dist = math.hypot(ex, ey)

        # --- Medição de Ângulo (Comum a todos) ---
        theta_meas = defines.KINEMATIC_THETA_SIGN * (
            current.theta + defines.KINEMATIC_THETA_OFFSET
        )

        # ================= 2. DELEGA CÁLCULOS =================

        vx_s, vy_s = self._compute_translational_velocity(mode, dx, dy, ex, ey, dist)

        # Passa o ângulo de alvo correto (seja de target_theta ou goal.theta)
        w, ang_err = self._compute_angular_velocity(
            mode, dist, target_angle_to_use, theta_meas
        )

        # ================= 3. CONDIÇÃO DE CHEGADA E PARADA (Inalterada) =================
        pos_tol = defines.CONTROL_POS_TOL
        ang_tol = defines.CONTROL_ANG_TOL

        chegou_pos = dist < pos_tol
        chegou_ang = abs(ang_err) < ang_tol

        # --- Lógica de Parada por Modo (Inalterada) ---
        if mode == "precision_movement":
            if chegou_pos and chegou_ang:
                return 0.0, 0.0, 0.0
            if chegou_pos:
                vx_s, vy_s = 0.0, 0.0
            if chegou_ang:
                w = 0.0

        elif mode == "rotation_only":
            vx_s, vy_s = 0.0, 0.0
            if chegou_ang:
                w = 0.0

        elif mode == "maintain_orientation":
            w = 0.0
            if chegou_pos:
                vx_s, vy_s = 0.0, 0.0

        return vx_s, vy_s, w

    def _compute_translational_velocity(self, mode, dx, dy, ex, ey, dist):
        """
        Calcula e retorna as velocidades translacionais (vx_s, vy_s)
        com base no modo de movimento.
        (ESTA FUNÇÃO ESTÁ INALTERADA)
        """
        # --- Carrega constantes globais ---
        k_pos = defines.CONTROL_K_POS
        vmax = defines.CONTROL_V_MAX
        v_min = defines.CONTROL_V_MIN
        pos_tol = defines.CONTROL_POS_TOL
        kd_pos = defines.GLOBAL_KD_POS

        vx_s, vy_s = 0.0, 0.0

        if mode == "precision_movement":
            now_lin = time.monotonic()
            st_lin = self._trans_state
            if st_lin["prev_time"] is None:
                dt_lin = defines.CONTROL_DEFAULT_DT
            else:
                dt_lin = max(defines.CONTROL_DT_EPSILON, now_lin - st_lin["prev_time"])
            st_lin["prev_time"] = now_lin

            if dist < pos_tol:
                st_lin["prev_ex"] = ex
                st_lin["prev_ey"] = ey
            else:
                d_ex = (ex - st_lin["prev_ex"]) / dt_lin
                d_ey = (ey - st_lin["prev_ey"]) / dt_lin
                st_lin["prev_ex"] = ex
                st_lin["prev_ey"] = ey

                vx_s = k_pos * ex + kd_pos * d_ex
                vy_s = k_pos * ey + kd_pos * d_ey

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
            if dist >= pos_tol:
                vx_s = k_pos * dx
                vy_s = k_pos * dy

                v = math.hypot(vx_s, vy_s)
                if v > vmax:
                    vx_s *= vmax / v
                    vy_s *= vmax / v
                    v = vmax
                if 0.0 < v < v_min:
                    vx_s *= v_min / v
                    vy_s *= v_min / v

        return vx_s, vy_s

    def _compute_angular_velocity(self, mode, dist, goal_theta, theta_meas):
        """
        Calcula e retorna a velocidade angular (w) e o erro angular (ang_err)
        com base no modo de movimento.
        (ESTA FUNÇÃO ESTÁ INALTERADA - ela recebe o 'goal_theta' correto)
        """
        # --- Carrega constantes globais ---
        k_ang = defines.CONTROL_K_ANG
        kd_ang = defines.CONTROL_KD_ANG_FUNC
        wmax = defines.CONTROL_W_MAX
        yaw_deadband = defines.CONTROL_YAW_DEADBAND

        w = 0.0

        if mode == "maintain_orientation":
            st_yaw = self._yaw_state
            st_yaw["prev_err"] = 0.0
            return 0.0, 0.0

        now_yaw = time.monotonic()
        st_yaw = self._yaw_state
        if st_yaw["prev_time"] is None:
            dt_yaw = defines.CONTROL_DEFAULT_DT
        else:
            dt_yaw = max(defines.CONTROL_DT_EPSILON, now_yaw - st_yaw["prev_time"])
        st_yaw["prev_time"] = now_yaw

        ang_err = Pose2D.normalize_angle_to_pi(goal_theta - theta_meas)

        if abs(ang_err) < yaw_deadband:
            st_yaw["prev_err"] = ang_err
            return 0.0, ang_err

        d_ang_err = (ang_err - st_yaw["prev_err"]) / dt_yaw
        st_yaw["prev_err"] = ang_err

        w = k_ang * ang_err + kd_ang * d_ang_err
        w = max(-wmax, min(wmax, w))
        return w, ang_err
