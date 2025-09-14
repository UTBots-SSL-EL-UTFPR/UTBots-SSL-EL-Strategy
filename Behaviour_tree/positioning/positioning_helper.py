import math
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from SSL_configuration.configuration import Configuration
from utils import defines
from utils.defines import Quadrant, QuadrantType, RoleType, ZoneType
from utils.pose2D import Pose2D

from ..core.World_State import RobotID, World_State

GOALKEEPER_DISTANCE_X = 2250
HALF_GOALKEEPER_AREA_WIDTH = 675
GOAL_LENGHT = 500

WALL_MARGIN = 200
KEEPER_MARGIN = 200
INFLUENCE_RADIUS = 500
GRID_STEP = 250

HALF_LEGHT = int(4500 / 2)
HALF_WID = int(3000 / 2)
MIN_PASS_DISTANCE = 1000

ROBOT_RADIUS = int(90)


class ShadowCone:
    def __init__(self, origin: Pose2D, opponent: Pose2D, radius=ROBOT_RADIUS):
        self.origin = origin
        self.opponent = opponent
        self.radius = radius
        self.radius_sq = radius**2

        self.vec_origin_to_opp = (opponent.x - origin.x, opponent.y - origin.y)
        self.dist_sq = self.vec_origin_to_opp[0] ** 2 + self.vec_origin_to_opp[1] ** 2

        self.origin_inside = self.dist_sq <= self.radius_sq

        if not self.origin_inside and self.dist_sq > self.radius_sq:
            dist = math.sqrt(self.dist_sq)

            ux = self.vec_origin_to_opp[0] / dist
            uy = self.vec_origin_to_opp[1] / dist

            cos_alpha = math.sqrt(self.dist_sq - self.radius_sq) / dist
            sin_alpha = self.radius / dist

            self.ray_left = (
                ux * cos_alpha - uy * sin_alpha,
                uy * cos_alpha + ux * sin_alpha,
            )
            self.ray_right = (
                ux * cos_alpha + uy * sin_alpha,
                uy * cos_alpha - ux * sin_alpha,
            )
        else:
            self.ray_left = (0, 0)
            self.ray_right = (0, 0)


class Positioning_helper:
    _instance = None
    _world_state = World_State.get_object()
    _configuration = Configuration.getObject()

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_object():
        if not Positioning_helper._instance:
            Positioning_helper._instance = Positioning_helper()
        return Positioning_helper._instance

    @staticmethod
    def distance_to_quadrant_border(pose: Pose2D, quad: Quadrant) -> float:

        dist_to_left_border = pose.x - quad.x_min
        dist_to_right_border = quad.x_max - pose.x
        dist_to_bottom_border = pose.y - quad.y_min
        dist_to_top_border = quad.y_max - pose.y
        return min(
            max(0, dist_to_left_border),
            max(0, dist_to_right_border),
            max(0, dist_to_bottom_border),
            max(0, dist_to_top_border),
        )

    @staticmethod
    def verify_quadrant_free(quad: Quadrant, max_dist_from_border: int) -> bool:
        all_robots: list[Pose2D]
        all_robots = Positioning_helper._world_state.get_all_foes_position()

        robots_in_quad = [
            position
            for position in all_robots
            if position.quadrant and position.quadrant.name == quad.name
        ]

        if not robots_in_quad:
            return True
        return all(
            Positioning_helper.distance_to_quadrant_border(robot, quad)
            <= max_dist_from_border
            for robot in robots_in_quad
        )

    @staticmethod
    def get_atack_quadrant_free(max_dist_from_border: int) -> list[QuadrantType]:
        """
        Retorna uma LISTA DE ENUMS (QuadrantType) dos quadrantes de ataque livres.
        """
        attack_zone_quadrants = ZoneType.ATTACK.value.quadrants
        free_quadrants_enums = []

        for q_data in attack_zone_quadrants:

            if Positioning_helper.verify_quadrant_free(q_data, max_dist_from_border):
                free_quadrants_enums.append(QuadrantType[q_data.name])

        return free_quadrants_enums

    @staticmethod
    def is_in_goalkeeper_area(pose: Pose2D, margin):
        y_in_range = (
            -HALF_GOALKEEPER_AREA_WIDTH - margin
            < pose.y
            < HALF_GOALKEEPER_AREA_WIDTH + margin
        )
        if not y_in_range:
            return False
        x_abs = abs(pose.x)
        x_in_range = (
            GOALKEEPER_DISTANCE_X - GOAL_LENGHT - margin
            < x_abs
            < GOALKEEPER_DISTANCE_X + margin
        )
        return x_in_range

    @staticmethod
    def outside_walls(pose: Pose2D, margin):
        return abs(pose.x) > 2250 - margin or abs(pose.y) > 1500 - margin

    @staticmethod
    def outside_enemies_influence(pose: Pose2D) -> bool:
        foes = Positioning_helper._world_state.get_all_foes_position()
        for e in foes:
            if pose.distance_to(e) < INFLUENCE_RADIUS:
                return False
        return True

    @staticmethod
    def is_point_in_shadow_vectorized(
        point: Pose2D, origin: Pose2D, shadow: ShadowCone
    ) -> bool:
        """
        Versão otimizada que verifica se um ponto está em uma sombra pré-calculada.
        """
        if shadow.origin_inside:
            return True

        vec_origin_to_point = (point.x - origin.x, point.y - origin.y)

        dot_product_direction = (
            vec_origin_to_point[0] * shadow.vec_origin_to_opp[0]
            + vec_origin_to_point[1] * shadow.vec_origin_to_opp[1]
        )
        if dot_product_direction < 0:
            return False

        cross_left = (
            shadow.ray_left[0] * vec_origin_to_point[1]
            - shadow.ray_left[1] * vec_origin_to_point[0]
        )
        cross_right = (
            shadow.ray_right[0] * vec_origin_to_point[1]
            - shadow.ray_right[1] * vec_origin_to_point[0]
        )

        return cross_left >= 0 and cross_right <= 0

    @staticmethod
    def find_largest_visible_square_vectorized(
        quadrant: Quadrant,
        shadows: List[ShadowCone],
        origin: Pose2D,
        grid_step: float = 100,
    ) -> Tuple[int, int, int] | None:
        """
        Encontra o maior quadrado visível usando matemática vetorial e busca binária.
        Recebe uma lista de 'shadows' pré-calculados para máxima eficiência.
        """
        best_square = (0, 0, 0)

        y = quadrant.y_min
        while y < quadrant.y_max:
            x = quadrant.x_min
            while x < quadrant.x_max:
                top_left_candidate = Pose2D(int(x), int(y))

                is_start_visible = True
                for s in shadows:
                    if Positioning_helper.is_point_in_shadow_vectorized(
                        top_left_candidate, origin, s
                    ):
                        is_start_visible = False
                        break

                if not is_start_visible:
                    x += grid_step
                    continue

                high = min(quadrant.x_max - x, quadrant.y_max - y)
                best_side_for_this_corner = 0

                if high > best_square[2]:
                    low = best_square[2]

                    while low <= high:
                        mid = round(((low + high) / 2) / grid_step) * grid_step
                        if mid <= best_side_for_this_corner:
                            break

                        corners = [
                            top_left_candidate,
                            Pose2D(int(x + mid), int(y)),
                            Pose2D(int(x), int(y + mid)),
                            Pose2D(int(x + mid), int(y + mid)),
                        ]
                        is_visible = True
                        for corner in corners:
                            for s in shadows:
                                if Positioning_helper.is_point_in_shadow_vectorized(
                                    corner, origin, s
                                ):
                                    is_visible = False
                                    break
                            if not is_visible:
                                break

                        if is_visible:
                            best_side_for_this_corner = mid
                            low = mid + grid_step
                        else:
                            high = mid - grid_step

                if best_side_for_this_corner > best_square[2]:
                    best_square = (int(x), int(y), int(best_side_for_this_corner))

                x += grid_step
            y += grid_step

        return best_square if best_square[2] > 0 else None

    @staticmethod
    def constrain_position(pose: Pose2D) -> Pose2D:
        """
        Limita uma Pose2D para que esteja dentro do campo e fora da área do goleiro adversário.
        """
        our_goal_is_negative_x = Positioning_helper._configuration.is_left_team

        clamped_x = Pose2D._clamp(
            pose.x, -HALF_LEGHT + WALL_MARGIN, HALF_LEGHT - WALL_MARGIN
        )
        clamped_y = Pose2D._clamp(
            pose.y, -HALF_WID + WALL_MARGIN, HALF_WID - WALL_MARGIN
        )

        constrained_pose = Pose2D(clamped_x, clamped_y)

        if our_goal_is_negative_x:
            gk_area_x_min = GOALKEEPER_DISTANCE_X - GOAL_LENGHT
            gk_area_x_max = HALF_LEGHT
        else:
            gk_area_x_min = -HALF_LEGHT
            gk_area_x_max = -(GOALKEEPER_DISTANCE_X - GOAL_LENGHT)

        gk_area_y_max = HALF_GOALKEEPER_AREA_WIDTH

        is_in_gk_x = (
            gk_area_x_min < constrained_pose.x < gk_area_x_max
            if our_goal_is_negative_x
            else gk_area_x_max < constrained_pose.x < gk_area_x_min
        )
        is_in_gk_y = abs(constrained_pose.y) < gk_area_y_max

        if is_in_gk_x and is_in_gk_y:
            dist_to_front_border = abs(constrained_pose.x - gk_area_x_min)
            dist_to_top_border = abs(constrained_pose.y - gk_area_y_max)
            dist_to_bottom_border = abs(constrained_pose.y - (-gk_area_y_max))

            min_dist = min(
                dist_to_front_border, dist_to_top_border, dist_to_bottom_border
            )

            if min_dist == dist_to_front_border:
                constrained_pose.x = gk_area_x_min - KEEPER_MARGIN
            elif min_dist == dist_to_top_border:
                constrained_pose.y = gk_area_y_max + KEEPER_MARGIN
            else:  # min_dist == dist_to_bottom_border
                constrained_pose.y = -gk_area_y_max - KEEPER_MARGIN
        return constrained_pose

    @staticmethod
    def find_largest_dual_visibility_square(
        quadrant: Quadrant,
        origin_kicker: Pose2D,
        origin_goal: Pose2D,
        opponents: List[Pose2D],
        grid_step: float = 100,
    ) -> Tuple[int, int, int] | None:
        """
        Encontra o maior quadrado que é visível SIMULTANEAMENTE a partir do
        cobrador (origin_kicker) e do gol (origin_goal).
        """
        shadows_from_kicker = [ShadowCone(origin_kicker, opp) for opp in opponents]
        shadows_from_goal = [ShadowCone(origin_goal, opp) for opp in opponents]
        best_square = (0, 0, 0)
        # for s in shadows_from_kicker:
        #     print(s.ray_left)
        #     print(s.ray_right)

        y = quadrant.y_min
        while y < quadrant.y_max:
            x = quadrant.x_min
            while x < quadrant.x_max:
                top_left_candidate = Pose2D(int(x), int(y))

                is_start_visible = True
                for s in shadows_from_kicker:
                    if Positioning_helper.is_point_in_shadow_vectorized(
                        top_left_candidate, origin_kicker, s
                    ):
                        is_start_visible = False
                        break
                if not is_start_visible:
                    x += grid_step
                    continue

                for s in shadows_from_goal:
                    if Positioning_helper.is_point_in_shadow_vectorized(
                        top_left_candidate, origin_goal, s
                    ):
                        is_start_visible = False
                        break

                if not is_start_visible:
                    x += grid_step
                    continue

                high = min(quadrant.x_max - x, quadrant.y_max - y)
                best_side_for_this_corner = 0

                if high > best_square[2]:
                    low = best_square[2]
                    while low <= high:
                        mid = round(((low + high) / 2) / grid_step) * grid_step
                        if mid <= best_side_for_this_corner:
                            break

                        corners = [
                            top_left_candidate,
                            Pose2D(int(x + mid), int(y)),
                            Pose2D(int(x), int(y + mid)),
                            Pose2D(int(x + mid), int(y + mid)),
                        ]

                        is_fully_visible = True
                        for corner in corners:
                            for s in shadows_from_kicker:
                                if Positioning_helper.is_point_in_shadow_vectorized(
                                    corner, origin_kicker, s
                                ):
                                    is_fully_visible = False
                                    break
                            if not is_fully_visible:
                                break

                            for s in shadows_from_goal:
                                if Positioning_helper.is_point_in_shadow_vectorized(
                                    corner, origin_goal, s
                                ):
                                    is_fully_visible = False
                                    break
                            if not is_fully_visible:
                                break

                        if is_fully_visible:
                            best_side_for_this_corner = mid
                            low = mid + grid_step
                        else:
                            high = mid - grid_step

                if best_side_for_this_corner > best_square[2]:
                    best_square = (int(x), int(y), int(best_side_for_this_corner))

                x += grid_step
            y += grid_step

        return best_square if best_square[2] > 0 else None

    # Dentro da classe Positioning_helper

    @staticmethod
    def find_best_point_in_square(
        square: Tuple[int, int, int],
        kicker_pos: Pose2D,
        ball_pos: Pose2D,
        goal_center: Pose2D,
        min_pass_dist: float,
        point_grid_step: float = 100.0,
    ) -> Pose2D | None:
        x_start, y_start, side = square
        if side == 0:
            return None
        print(square)
        valid_points = []

        y = y_start
        while y <= y_start + side:
            x = x_start
            while x <= x_start + side:
                candidate = Pose2D(int(x), int(y))

                dist_to_kicker = candidate.distance_to(kicker_pos)
                is_advanced_enough = candidate.x >= ball_pos.x

                if dist_to_kicker >= min_pass_dist and is_advanced_enough:
                    valid_points.append(candidate)

                x += point_grid_step
            y += point_grid_step

        if not valid_points:
            return None

        best_point = min(valid_points, key=lambda p: p.distance_to(goal_center))
        return best_point

    @staticmethod
    def find_safest_point_in_square(
        square: Tuple[int, int, int],
        kicker_pos: Pose2D,
        ball_pos: Pose2D,
        opponents: List[Pose2D],
        min_pass_dist: float,
        point_grid_step: float = 100.0,
    ) -> Pose2D | None:
        """
        Busca dentro de um quadrado o ponto que maximiza a distância para o oponente mais próximo,
        respeitando as restrições de passe e de posição em relação à bola.
        """
        x_start, y_start, side = square
        if side == 0:
            return None

        valid_points = []

        y = y_start
        while y <= y_start + side:
            x = x_start
            while x <= x_start + side:
                candidate = Pose2D(int(x), int(y))
                dist_to_kicker = candidate.distance_to(kicker_pos)
                is_advanced_enough = candidate.x >= ball_pos.x

                if dist_to_kicker >= min_pass_dist and is_advanced_enough:
                    valid_points.append(candidate)

                x += point_grid_step
            y += point_grid_step

        if not valid_points:
            return None
        safest_point = None
        max_safety_distance = -1

        for point in valid_points:
            if not opponents:
                min_dist_to_opponent = float("inf")
            else:
                min_dist_to_opponent = min(
                    [point.distance_to(opp) for opp in opponents]
                )

            if min_dist_to_opponent > max_safety_distance:
                max_safety_distance = min_dist_to_opponent
                safest_point = point

        return safest_point

    @staticmethod
    def _distance_point_to_segment_sq(p: Pose2D, v: Pose2D, w: Pose2D) -> float:
        """
        Calcula a distância ao quadrado de um ponto 'p' a um segmento de reta 'v-w'.
        É um cálculo geométrico padrão para encontrar a menor distância.
        """
        l2 = v.distance_to_sq(w)
        if l2 == 0.0:
            return p.distance_to_sq(v)

        dot_product = (p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)
        t = max(0, min(1, dot_product / l2))

        # Calcula as coordenadas do ponto projetado no segmento de reta
        projection_x = v.x + t * (w.x - v.x)
        projection_y = v.y + t * (w.y - v.y)

        return (p.x - projection_x) ** 2 + (p.y - projection_y) ** 2

    # Dentro da sua classe Positioning_helper

    @staticmethod
    def _project_point_on_ray(
        point: Pose2D, ray_origin: Pose2D, ray_direction: Tuple[float, float]
    ) -> Pose2D:
        """
        Projeta um ponto em um raio infinito. Essencial para encontrar o ponto mais
        próximo na borda de um cone de sombra.
        """
        # Vetor da origem do raio para o ponto que queremos projetar
        vec_to_point_x = point.x - ray_origin.x
        vec_to_point_y = point.y - ray_origin.y

        dir_x, dir_y = ray_direction

        # O produto escalar nos dá o comprimento da projeção ao longo da direção do raio
        dot_product = vec_to_point_x * dir_x + vec_to_point_y * dir_y

        # Usamos max(0, ...) para garantir que a projeção esteja no raio
        # e não "atrás" da sua origem.
        t = max(0, dot_product)

        return Pose2D(int(ray_origin.x + t * dir_x), int(ray_origin.y + t * dir_y))

    @staticmethod
    def is_path_clear(
        start_pos: Pose2D,
        end_pos: Pose2D,
        opponents: List[Pose2D],
        robot_radius: float = 90.0,
    ) -> bool:
        """
        Função auxiliar que verifica de forma simples se o caminho entre dois pontos está livre.
        Retorna True se estiver livre, False se estiver obstruído.
        """
        if not opponents:
            return True
        collision_dist_sq = (robot_radius + robot_radius) ** 2

        for opp in opponents:
            dist_sq = Positioning_helper._distance_point_to_segment_sq(
                opp, start_pos, end_pos
            )
            if dist_sq < collision_dist_sq:
                return False
        return True

    @staticmethod
    def get_clear_pass_position(robot_pos: Pose2D) -> Tuple[bool, Pose2D]:
        """
        Verifica a visibilidade e, se obstruído, calcula o ponto visível mais próximo
        da posição atual do robô, saindo do cone de sombra do bloqueador.
        """
        ball_pos = Positioning_helper._world_state.get_ball_position()
        all_robots = Positioning_helper._world_state.get_all_robot_position()
        obstacles = [obs for obs in all_robots if obs != robot_pos]

        if Positioning_helper.is_path_clear(
            ball_pos, robot_pos, obstacles, ROBOT_RADIUS
        ):
            return True, ball_pos

        collision_dist_sq = (ROBOT_RADIUS + ROBOT_RADIUS) ** 2
        blockers = []
        for obs in obstacles:
            if (
                Positioning_helper._distance_point_to_segment_sq(
                    obs, ball_pos, robot_pos
                )
                < collision_dist_sq
            ):
                blockers.append(obs)

        if not blockers:
            return True, ball_pos

        main_blocker = min(blockers, key=lambda b: b.distance_to_sq(robot_pos))

        # 4. Cria o "Cone de Sombra Inflado"
        inflated_shadow = ShadowCone(ball_pos, main_blocker, ROBOT_RADIUS * 2 + 50)

        if inflated_shadow.origin_inside:
            return False, robot_pos

        # 5. Projeta a posição atual do robô nas duas bordas do cone de sombra inflado
        left_ray_dir = inflated_shadow.ray_left
        right_ray_dir = inflated_shadow.ray_right
        norm_left = math.hypot(*left_ray_dir)
        norm_right = math.hypot(*right_ray_dir)

        if norm_left == 0 or norm_right == 0:
            return False, robot_pos  # Evita divisão por zero

        left_ray_dir_unit = (left_ray_dir[0] / norm_left, left_ray_dir[1] / norm_left)
        right_ray_dir_unit = (
            right_ray_dir[0] / norm_right,
            right_ray_dir[1] / norm_right,
        )

        escape_point1 = Positioning_helper._project_point_on_ray(
            robot_pos, ball_pos, left_ray_dir_unit
        )
        escape_point2 = Positioning_helper._project_point_on_ray(
            robot_pos, ball_pos, right_ray_dir_unit
        )

        # 6. Escolhe o ponto de escape que está mais perto da posição atual do robô
        dist1_sq = robot_pos.distance_to_sq(escape_point1)
        dist2_sq = robot_pos.distance_to_sq(escape_point2)

        best_escape_point = escape_point1 if dist1_sq < dist2_sq else escape_point2

        return False, best_escape_point

    @staticmethod
    def get_goal_center() -> Pose2D:
        config = Configuration.getObject()
        goal_pose = Pose2D(2250, 0)
        goal_pose.x *= config.get_side_sign()
        return goal_pose

    @staticmethod
    def compute_pose_facing_goal(target_position: Pose2D) -> Pose2D:
        """
        Calcula uma Pose2D no ponto-alvo, orientada para o centro do gol.
        """
        tx: int = 0
        ty: int = 0
        tx, ty, _ = target_position

        goal = Positioning_helper.get_goal_center()

        gx, gy, _ = goal
        theta = math.atan2(gy - ty, gx - tx)

        return Pose2D(tx, ty, int(theta))

    @staticmethod
    def calculate_rebound_position(robot_position: Pose2D) -> Pose2D:
        """
        Calcula uma posição para um rebote, assumindo um chute
        A lógica não usa a velocidade da bola, apenas as posições.
        """
        opponents = Positioning_helper._world_state.get_all_foes_position()
        potential_blockers = []
        robot_radius = ROBOT_RADIUS
        shot_corridor_width_sq = (robot_radius * 2) ** 2
        s = Positioning_helper._configuration.get_side_sign()
        kicker_pos = Positioning_helper._world_state.get_ball_position()
        goal_center = Positioning_helper.get_goal_center()
        for opp in opponents:
            dist_sq = Positioning_helper._distance_point_to_segment_sq(
                opp, kicker_pos, goal_center
            )
            if dist_sq < shot_corridor_width_sq:
                potential_blockers.append(opp)

        if not potential_blockers:
            return Pose2D(1500 * s, 0)

        primary_blocker = min(
            potential_blockers, key=lambda b: b.distance_to_sq(robot_position)
        )

        # --- Prever a trajetória do rebote --- #
        vec_in_x = primary_blocker.x - kicker_pos.x
        vec_in_y = primary_blocker.y - kicker_pos.y

        normal_x = kicker_pos.x - primary_blocker.x
        normal_y = kicker_pos.y - primary_blocker.y
        norm_mag = math.hypot(normal_x, normal_y)

        if norm_mag == 0:
            return Pose2D(1500 * s, 0)

        normal_x /= norm_mag
        normal_y /= norm_mag

        # Fórmula da reflexão: R = V - 2 * (V · N) * N (nao sei gaal)
        dot_product = vec_in_x * normal_x + vec_in_y * normal_y

        vec_out_x = vec_in_x - 2 * dot_product * normal_x
        vec_out_y = vec_in_y - 2 * dot_product * normal_y

        # --- Definir o ponto de espera ---

        rebound_mag = math.hypot(vec_out_x, vec_out_y)
        if rebound_mag == 0:
            return Pose2D(1500 * s, 0)

        rebound_dir_x = vec_out_x / rebound_mag
        rebound_dir_y = vec_out_y / rebound_mag

        intercept_distance = (
            500  # Distância que o suporte deve esperar do local da colisão
        )
        rebound_pos = Pose2D(
            primary_blocker.x + rebound_dir_x * intercept_distance,
            primary_blocker.y + rebound_dir_y * intercept_distance,
        )

        pos = Positioning_helper.constrain_position(rebound_pos)

        return pos

    
    @staticmethod
    def get_best_pass_orientation(
        passer_pos: Pose2D,
        receiver_pos: Pose2D,
        goal_pos: Pose2D,
        opponents: List[Pose2D],
        weight_receive: float = 0.6,
        weight_goal: float = 0.4
    ) -> float:
        """
        Retorna o melhor ângulo (em radianos) para o receptor se orientar ao receber o passe.

        - passer_pos: posição do robô passador
        - receiver_pos: posição do robô receptor
        - goal_pos: centro do gol adversário
        - opponents: lista de posições dos oponentes
        - weight_receive: peso da orientação para receber o passe
        - weight_goal: peso da orientação futura para finalizar ou progredir

        Retorna um ângulo em radianos (orientação ideal do receptor).
        """

        # Vetor da bola para o receptor (direção de recepção)
        vec_receive = (passer_pos.x - receiver_pos.x, passer_pos.y - receiver_pos.y)
        angle_receive = math.atan2(vec_receive[1], vec_receive[0])

        # Vetor do receptor para o gol (direção ofensiva)
        vec_goal = (goal_pos.x - receiver_pos.x, goal_pos.y - receiver_pos.y)
        angle_goal = math.atan2(vec_goal[1], vec_goal[0])

        # Combinação ponderada dos ângulos (mantém continuidade da jogada)
        best_angle = math.atan2(
            weight_receive * math.sin(angle_receive) + weight_goal * math.sin(angle_goal),
            weight_receive * math.cos(angle_receive) + weight_goal * math.cos(angle_goal)
        )

        # Ajuste de segurança: verificar se caminho está livre até o receptor
        if not Positioning_helper.is_path_clear(passer_pos, receiver_pos, opponents):
            # Se caminho bloqueado, orientar receptor para bola diretamente (prioridade em receber)
            return angle_receive

        return best_angle

    @staticmethod
    def are_pass_orientations_aligned(
        passer_id: RobotID,
        receiver_id: RobotID,
        goal_pos: Pose2D,
        opponents: List[Pose2D],
        tolerance_deg: float = 10.0
    ) -> bool:
        """
        Verifica se passador e receptor estão orientados corretamente para o passe.

        - Passador: deve estar orientado em direção ao receptor.
        - Receptor: deve estar orientado segundo o melhor ângulo (receber + progressão).

        :param passer_id: Robô que irá passar a bola.
        :param receiver_id: Robô que irá receber a bola.
        :param goal_pos: Posição do gol adversário.
        :param opponents: Lista de posições dos adversários.
        :param tolerance_deg: Tolerância angular em graus.
        :return: True se ambos estiverem alinhados.
        """
        ws = World_State.get_object()

        passer_pose = ws.get_team_robot_pose(passer_id.value)
        receiver_pose = ws.get_team_robot_pose(receiver_id.value)

        if passer_pose is None or receiver_pose is None:
            return False

        # --- Passador deve olhar pro receptor ---
        desired_passer_angle = math.atan2(
            receiver_pose.y - passer_pose.y,
            receiver_pose.x - passer_pose.x
        )

        # --- Receptor deve estar alinhado para receber + olhar pro gol ---
        desired_receiver_angle = Positioning_helper.get_best_pass_orientation(
            passer_pos=passer_pose,
            receiver_pos=receiver_pose,
            goal_pos=goal_pos,
            opponents=opponents
        )

        tolerance_rad = math.radians(tolerance_deg)

        def angle_diff(a, b):
            return math.atan2(math.sin(a - b), math.cos(a - b))

        passer_aligned = abs(angle_diff(desired_passer_angle, passer_pose.theta)) <= tolerance_rad
        receiver_aligned = abs(angle_diff(desired_receiver_angle, receiver_pose.theta)) <= tolerance_rad

        return passer_aligned and receiver_aligned