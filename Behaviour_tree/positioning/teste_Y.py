# Imports necessários para o teste
import timeit
from dataclasses import dataclass
import math
from typing import List, Tuple

# ==============================================================================
# CLASSES FALSAS (MOCKS) PARA PERMITIR A EXECUÇÃO INDEPENDENTE DO ARQUIVO
# ==============================================================================
@dataclass
class MockPose2D:
    x: float
    y: float

    def distance_to_sq(self, other: 'MockPose2D') -> float:
        """Calcula a distância ao quadrado para evitar sqrt."""
        return (self.x - other.x)**2 + (self.y - other.y)**2
        
    def __str__(self):
        return f"({self.x:.0f}, {self.y:.0f})"

# Substituindo a dependência real por nossa classe mock
Pose2D = MockPose2D

# ==============================================================================
# CLASSE E FUNÇÕES
# ==============================================================================

class Positioning_helper:
    """Classe que contém as funções de ajuda para posicionamento."""

    @staticmethod
    def _distance_point_to_segment_sq(p: Pose2D, v: Pose2D, w: Pose2D) -> float:
        """Calcula a distância ao quadrado de um ponto 'p' a um segmento de reta 'v-w'."""
        l2 = v.distance_to_sq(w)
        if l2 == 0.0:
            return p.distance_to_sq(v)
        
        dot_product = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y))
        t = max(0, min(1, dot_product / l2))
        
        projection_x = v.x + t * (w.x - v.x)
        projection_y = v.y + t * (w.y - v.y)
        
        return (p.x - projection_x)**2 + (p.y - projection_y)**2

    @staticmethod
    def is_robot_fully_visible_from_ball(
        robot_pos: Pose2D, 
        ball_pos: Pose2D, 
        opponents: List[Pose2D],
        robot_radius: float = 90.0,
        opponent_radius: float = 90.0
    ) -> bool:
        """Verifica se a linha de passe está livre, retornando True ou False."""
        if not opponents:
            return True
            
        collision_dist_sq = (robot_radius + opponent_radius)**2
        
        for opp in opponents:
            dist_sq = Positioning_helper._distance_point_to_segment_sq(opp, ball_pos, robot_pos)
            if dist_sq < collision_dist_sq:
                return False

        return True

    # =================================================================
    # ========= FUNÇÃO ADICIONADA CONFORME SOLICITADO =========
    # =================================================================
    @staticmethod
    def get_pass_visibility_and_alternative(
        robot_pos: Pose2D, 
        ball_pos: Pose2D, 
        opponents: List[Pose2D],
        robot_radius: float = 90.0,
        opponent_radius: float = 90.0
    ) -> Tuple[bool, Pose2D]:
        """
        Verifica a visibilidade entre um robô e a bola.
        - Se visível, retorna (True, ball_pos).
        - Se obstruído, retorna (False, melhor_posicao_alternativa), onde a posição
          alternativa é o ponto mais próximo do robô que contorna o obstáculo.
        """
        if not opponents:
            return True, ball_pos

        collision_dist_sq = (robot_radius + opponent_radius)**2
        
        blockers = []
        for opp in opponents:
            dist_sq = Positioning_helper._distance_point_to_segment_sq(opp, ball_pos, robot_pos)
            if dist_sq < collision_dist_sq:
                blockers.append(opp)

        if not blockers:
            return True, ball_pos

        main_blocker = min(blockers, key=lambda b: b.distance_to_sq(robot_pos))

        pass_vec_x = robot_pos.x - ball_pos.x
        pass_vec_y = robot_pos.y - ball_pos.y
        pass_dist = math.hypot(pass_vec_x, pass_vec_y)

        if pass_dist == 0:
            return False, robot_pos

        perp_vec_x = -pass_vec_y / pass_dist
        perp_vec_y = pass_vec_x / pass_dist
        
        escape_distance = robot_radius + opponent_radius + 50 # 50mm de margem

        escape_point1 = Pose2D(main_blocker.x + perp_vec_x * escape_distance,
                               main_blocker.y + perp_vec_y * escape_distance)
                           
        escape_point2 = Pose2D(main_blocker.x - perp_vec_x * escape_distance,
                               main_blocker.y - perp_vec_y * escape_distance)

        dist1_sq = robot_pos.distance_to_sq(escape_point1)
        dist2_sq = robot_pos.distance_to_sq(escape_point2)
        
        best_escape_point = escape_point1 if dist1_sq < dist2_sq else escape_point2
        
        return False, best_escape_point

# ==============================================================================
# BLOCO DE TESTE
# ==============================================================================
if __name__ == '__main__':
    
    def testar_visibilidade_com_alternativa():
        print("--- Teste Funcional: get_pass_visibility_and_alternative ---")
        
        # --- Cenário Base ---
        robot_pos = Pose2D(1500, 500)
        ball_pos = Pose2D(-1000, 200)

        # --- Teste 1: Caminho Livre ---
        print("\n--- Cenário 1: Caminho Livre ---")
        opponents_livre = [Pose2D(3000, 0)] # Oponente longe
        is_visible, pose = Positioning_helper.get_pass_visibility_and_alternative(robot_pos, ball_pos, opponents_livre)
        print(f"Resultado: Visível? {is_visible} (Esperado: True)")
        print(f"  -> Posição Sugerida: {pose}")

        # --- Teste 2: Caminho Obstruído ---
        print("\n--- Cenário 2: Caminho Obstruído ---")
        opponents_obstruido = [Pose2D(200, 350)] # Oponente no meio
        is_visible, pose = Positioning_helper.get_pass_visibility_and_alternative(robot_pos, ball_pos, opponents_obstruido)
        print(f"Resultado: Visível? {is_visible} (Esperado: False)")
        print(f"  -> Posição Sugerida: {pose}")
        
        # --- Teste 3: Oponente Próximo, mas Fora do Caminho ---
        print("\n--- Cenário 3: Oponente Próximo mas Fora do Caminho ---")
        opponents_perto = [Pose2D(200, 100)] # Oponente abaixo da linha de passe
        is_visible, pose = Positioning_helper.get_pass_visibility_and_alternative(robot_pos, ball_pos, opponents_perto)
        print(f"Resultado: Visível? {is_visible} (Esperado: True)")
        print(f"  -> Posição Sugerida: {pose}")

    # ===============================================
    # EXECUÇÃO DO TESTE
    # ===============================================
    testar_visibilidade_com_alternativa()