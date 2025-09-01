# Imports necessários para o teste
import timeit
import numba # type: ignore
from dataclasses import dataclass

# ==============================================================================
# CLASSES FALSAS (MOCKS) PARA PERMITIR A EXECUÇÃO INDEPENDENTE DO ARQUIVO
# ==============================================================================
@dataclass
class MockPose2D:
    x: float
    y: float

@dataclass
class MockQuadrant:
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float

# Substituindo a dependência real por nossa classe mock
Pose2D = MockPose2D
Quadrant = MockQuadrant

# ==============================================================================
# CLASSES E FUNÇÕES A SEREM TESTADAS
# ==============================================================================
import math
from typing import List, Tuple

class ShadowCone:
    def __init__(self, origin: Pose2D, opponent: Pose2D, robot_radius: int = 80):
        self.origin = origin
        self.opponent = opponent
        self.radius = robot_radius
        self.radius_sq = robot_radius ** 2

        self.vec_origin_to_opp = (opponent.x - origin.x, opponent.y - origin.y)
        self.dist_sq = self.vec_origin_to_opp[0]**2 + self.vec_origin_to_opp[1]**2
        
        self.origin_inside = self.dist_sq <= self.radius_sq
        
        if not self.origin_inside and self.dist_sq > self.radius_sq:
            dist = math.sqrt(self.dist_sq)
            ux = self.vec_origin_to_opp[0] / dist
            uy = self.vec_origin_to_opp[1] / dist
            cos_alpha = math.sqrt(self.dist_sq - self.radius_sq) / dist
            sin_alpha = self.radius / dist
            self.ray_left = (ux * cos_alpha - uy * sin_alpha, uy * cos_alpha + ux * sin_alpha)
            self.ray_right = (ux * cos_alpha + uy * sin_alpha, uy * cos_alpha - ux * sin_alpha)
        else:
            self.ray_left = (0,0)
            self.ray_right = (0,0)

class Positioning_helper:
    # =================================
    # VERSÃO ORIGINAL (LENTA)
    # =================================
    @staticmethod
    def is_point_in_shadow(point: Pose2D, origin: Pose2D, opponent: Pose2D) -> bool:
        vec_origin_to_opp = (opponent.x - origin.x, opponent.y - origin.y)
        dist_origin_to_opp_sq = vec_origin_to_opp[0]**2 + vec_origin_to_opp[1]**2
        if dist_origin_to_opp_sq <= 80**2: return True
        dist_sqrt = math.sqrt(dist_origin_to_opp_sq)
        if dist_sqrt == 0: return True
        angle_alpha = math.asin(80 / dist_sqrt)
        vec_origin_to_point = (point.x - origin.x, point.y - origin.y)
        dist_origin_to_point = math.hypot(*vec_origin_to_point)
        if dist_origin_to_point == 0: return True
        cos_arg = (vec_origin_to_opp[0] * vec_origin_to_point[0] + vec_origin_to_point[1] * vec_origin_to_point[1]) / (dist_sqrt * dist_origin_to_point)
        cos_arg_clamped = max(-1.0, min(1.0, cos_arg))
        angle_beta = math.acos(cos_arg_clamped)
        return angle_beta < angle_alpha
    
    @staticmethod
    def is_square_visible(top_left: Pose2D, side: int, origin: Pose2D, opponents: list[Pose2D]) -> bool:
        if side <= 0: return True
        corners = [top_left, Pose2D(top_left.x + side, top_left.y), Pose2D(top_left.x, top_left.y + side), Pose2D(top_left.x + side, top_left.y + side)]
        for corner in corners:
            for opp in opponents:
                if Positioning_helper.is_point_in_shadow(corner, origin, opp):
                    return False
        return True

    @staticmethod
    def find_largest_visible_square(quadrant: Quadrant,origin: Pose2D,opponents: list[Pose2D], grid_step: float = 100):
        best_square = (0, 0, 0)
        y = quadrant.y_min
        while y < quadrant.y_max:
            x = quadrant.x_min
            while x < quadrant.x_max:
                top_left_candidate = Pose2D(int(x), int(y))
                is_start_visible = True
                for opp in opponents:
                    if Positioning_helper.is_point_in_shadow(top_left_candidate, origin, opp):
                        is_start_visible = False; break
                if not is_start_visible:
                    x += grid_step; continue
                max_possible_side = min(quadrant.x_max - x, quadrant.y_max - y)
                current_side = best_square[2]
                while current_side <= max_possible_side:
                    if Positioning_helper.is_square_visible(top_left_candidate, int(current_side), origin, opponents):
                        if current_side > best_square[2]:
                            best_square = (int(x), int(y), int(current_side))
                        current_side += grid_step 
                    else: break 
                x += grid_step
            y += grid_step
        return best_square if best_square[2] > 0 else None

    # =================================
    # VERSÃO OTIMIZADA (VISÃO SIMPLES)
    # =================================
    @staticmethod
    def is_point_in_shadow_vectorized(point: Pose2D, origin: Pose2D, shadow: ShadowCone) -> bool:
        if shadow.origin_inside: return True
        vec_origin_to_point = (point.x - origin.x, point.y - origin.y)
        dot_product_direction = (vec_origin_to_point[0] * shadow.vec_origin_to_opp[0] + vec_origin_to_point[1] * shadow.vec_origin_to_opp[1])
        if dot_product_direction < 0: return False
        cross_left = shadow.ray_left[0] * vec_origin_to_point[1] - shadow.ray_left[1] * vec_origin_to_point[0]
        cross_right = shadow.ray_right[0] * vec_origin_to_point[1] - shadow.ray_right[1] * vec_origin_to_point[0]
        return cross_left >= 0 and cross_right <= 0

    @staticmethod
    def find_largest_visible_square_vectorized(quadrant: Quadrant, shadows: List[ShadowCone], origin: Pose2D, grid_step: float = 100):
        best_square = (0, 0, 0)
        y = quadrant.y_min
        while y < quadrant.y_max:
            x = quadrant.x_min
            while x < quadrant.x_max:
                top_left_candidate = Pose2D(int(x), int(y))
                is_start_visible = True
                for s in shadows:
                    if Positioning_helper.is_point_in_shadow_vectorized(top_left_candidate, origin, s):
                        is_start_visible = False; break
                if not is_start_visible:
                    x += grid_step; continue
                high = min(quadrant.x_max - x, quadrant.y_max - y)
                best_side_for_this_corner = 0
                if high > best_square[2]:
                    low = best_square[2]
                    while low <= high:
                        mid = round(((low + high) / 2) / grid_step) * grid_step
                        if mid <= best_side_for_this_corner: break
                        corners = [top_left_candidate, Pose2D(x + mid, y), Pose2D(x, y + mid), Pose2D(x + mid, y + mid)]
                        is_visible = True
                        for corner in corners:
                            for s in shadows:
                                if Positioning_helper.is_point_in_shadow_vectorized(corner, origin, s):
                                    is_visible = False; break
                            if not is_visible: break
                        if is_visible:
                            best_side_for_this_corner = mid
                            low = mid + grid_step
                        else: high = mid - grid_step
                if best_side_for_this_corner > best_square[2]:
                    best_square = (int(x), int(y), int(best_side_for_this_corner))
                x += grid_step
            y += grid_step
        return best_square if best_square[2] > 0 else None

    # =================================
    # NOVA VERSÃO OTIMIZADA (VISÃO DUPLA)
    # =================================
    @staticmethod
    def find_largest_dual_visibility_square(quadrant: Quadrant, origin_kicker: Pose2D, origin_goal: Pose2D, opponents: List[Pose2D], grid_step: float = 100):
        shadows_from_kicker = [ShadowCone(origin_kicker, opp) for opp in opponents]
        shadows_from_goal = [ShadowCone(origin_goal, opp) for opp in opponents]
        best_square = (0, 0, 0)
        y = quadrant.y_min
        while y < quadrant.y_max:
            x = quadrant.x_min
            while x < quadrant.x_max:
                top_left_candidate = Pose2D(int(x), int(y))
                is_start_visible = True
                for s in shadows_from_kicker:
                    if Positioning_helper.is_point_in_shadow_vectorized(top_left_candidate, origin_kicker, s):
                        is_start_visible = False; break
                if not is_start_visible:
                    x += grid_step; continue
                for s in shadows_from_goal:
                    if Positioning_helper.is_point_in_shadow_vectorized(top_left_candidate, origin_goal, s):
                        is_start_visible = False; break
                if not is_start_visible:
                    x += grid_step; continue
                high = min(quadrant.x_max - x, quadrant.y_max - y)
                best_side_for_this_corner = 0
                if high > best_square[2]:
                    low = best_square[2]
                    while low <= high:
                        mid = round(((low + high) / 2) / grid_step) * grid_step
                        if mid <= best_side_for_this_corner: break
                        corners = [top_left_candidate, Pose2D(x + mid, y), Pose2D(x, y + mid), Pose2D(x + mid, y + mid)]
                        is_fully_visible = True
                        for corner in corners:
                            for s in shadows_from_kicker:
                                if Positioning_helper.is_point_in_shadow_vectorized(corner, origin_kicker, s):
                                    is_fully_visible = False; break
                            if not is_fully_visible: break
                            for s in shadows_from_goal:
                                if Positioning_helper.is_point_in_shadow_vectorized(corner, origin_goal, s):
                                    is_fully_visible = False; break
                            if not is_fully_visible: break
                        if is_fully_visible:
                            best_side_for_this_corner = mid
                            low = mid + grid_step
                        else: high = mid - grid_step
                if best_side_for_this_corner > best_square[2]:
                    best_square = (int(x), int(y), int(best_side_for_this_corner))
                x += grid_step
            y += grid_step
        return best_square if best_square[2] > 0 else None

# ==============================================================================
# BLOCO DE TESTE DE DESEMPENHO
# ==============================================================================
if __name__ == '__main__':
    
    def criar_cenario_teste() -> Tuple[Quadrant, Pose2D, Pose2D, List[Pose2D]]:
        """Cria um cenário de teste realista e consistente."""
        quadrante = Quadrant("Q7", 0, -500, 1125, 500)
        origem_chutador = Pose2D(-4000, 100)
        origem_gol = Pose2D(2250, 0) # Ponto de vista do centro do gol
        oponentes = [
            Pose2D(-1500, 750), Pose2D(-2500, 200), Pose2D(500, 0),
            Pose2D(800, -400), Pose2D(1000, 400), Pose2D(-500, -300)
        ]
        return quadrante, origem_chutador, origem_gol, oponentes

    print("🚀 Iniciando teste de desempenho comparativo...")
    
    # Setup para o timeit
    setup_code = """
from __main__ import Positioning_helper, criar_cenario_teste, Quadrant, Pose2D, ShadowCone
cenario_quadrante, cenario_origem_chutador, cenario_origem_gol, cenario_oponentes = criar_cenario_teste()
# Pré-cálculo para a versão de visão simples
shadows_precalculados = [ShadowCone(cenario_origem_chutador, opp) for opp in cenario_oponentes]
"""

    # Código a ser testado
    codigo_original = "Positioning_helper.find_largest_visible_square(cenario_quadrante, cenario_origem_chutador, cenario_oponentes, grid_step=100)"
    codigo_otimizado_simples = "Positioning_helper.find_largest_visible_square_vectorized(cenario_quadrante, shadows_precalculados, cenario_origem_chutador, grid_step=100)"
    codigo_otimizado_duplo = "Positioning_helper.find_largest_dual_visibility_square(cenario_quadrante, cenario_origem_chutador, cenario_origem_gol, cenario_oponentes, grid_step=100)"

    num_execucoes = 500
    print(f"Executando cada versão {num_execucoes} vezes...")

    # Medindo o tempo
    tempo_original = timeit.timeit(stmt=codigo_original, setup=setup_code, number=num_execucoes) / num_execucoes
    tempo_otimizado_simples = timeit.timeit(stmt=codigo_otimizado_simples, setup=setup_code, number=num_execucoes) / num_execucoes
    tempo_otimizado_duplo = timeit.timeit(stmt=codigo_otimizado_duplo, setup=setup_code, number=num_execucoes) / num_execucoes

    print("\n--- Resultados ---")
    print(f"Versão Original (Trigonometria)..: {tempo_original:.6f} segundos por execução")
    print(f"Otimizada (Visão Simples).......: {tempo_otimizado_simples:.6f} segundos por execução")
    print(f"Otimizada (Visão Dupla).........: {tempo_otimizado_duplo:.6f} segundos por execução")
    
    # Análise de Desempenho
    if tempo_otimizado_simples > 0:
        ganho_simples = tempo_original / tempo_otimizado_simples
        print(f"\n✅ A visão simples vetorizada foi {ganho_simples:.2f} vezes mais rápida que a original.")

    if tempo_otimizado_duplo > 0 and tempo_otimizado_simples > 0:
        custo_duplo = tempo_otimizado_duplo / tempo_otimizado_simples
        print(f"🔍 O custo da verificação dupla foi de {custo_duplo:.2f}x (a visão dupla é {custo_duplo:.2f} vezes mais lenta que a visão simples).")