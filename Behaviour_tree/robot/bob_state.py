from ..core.World_State import World_State, RobotID
from ..core import event_callbacks

from .all_bob_states import AllBobs_State

from utils.pose2D import Pose2D
from SSL_configuration.configuration import Configuration
from utils.defines import (
    ALL_QUADRANTS,
    Quadrant_type,
    RoleType,
    BALL_POSSESSION_DISTANCE, #verificar om configuration
)
#TODO
#   linha 82
#


class Bob_State:
    """Estado dinâmico do robô (posição, velocidade, posse, quadrante e role)."""
    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id

        self.world_state = World_State.get_object()
        self.configuration = Configuration.getObject()

        self.position: Pose2D = Pose2D(3333,3333)
        self.velocity: Pose2D = Pose2D()

        self.target_position: Pose2D | None = Pose2D()

        self.active_function = None
        self.current_command = None
        self.role: RoleType | None = None

        self.has_ball = False
        self.position_rept = 0

    
    def setup_callbacks(self):

        event_callbacks.lost_ball_posetion(self.robot_id.name)
        event_callbacks.new_quadrant(self.robot_id.name, 0)
        event_callbacks.new_zone(self.robot_id.name, 0)
        event_callbacks.on_robot_stuck(self.robot_id.name)
    #---------------------------------------------------------------------------------------#
    #                                       UPDATE                                          #
    # temos os seguintes eventos:                                                           #
    #   1. Mudança de posse de bola                                                         #
    #   3. Verifica target_position + repetição de target
    #---------------------------------------------------------------------------------------#

    def update(self):
        
        ################# Verifica se a posse de bola foi alterada #################
        if self.has_ball != self.check_ball_possession():
            #evento em bob_manager/strategy tree
            if(self.has_ball):
                event_callbacks.lost_ball_posetion(self.robot_id.name)
            else:
                event_callbacks.team_got_ball_posetion(self.robot_id.name)
            self.has_ball = not self.has_ball

        #################   Verifica se preso na mesma pos e verifica quadrante   #################
        new_pos = self.world_state.get_team_robot_pose(self.robot_id.value)
        if  self.position ==  new_pos:
            self.position_rept +=1
        else:
            self.position_rept = 0
            #---------------------quadrante---------------------#
            if new_pos.get_quadrant() != self.position.quadrant:
                event_callbacks.new_quadrant(self.robot_id.name, new_pos.quadrant)
                if new_pos.get_zone() != self.position.get_zone():
                    event_callbacks.new_zone(self.robot_id.name, new_pos.get_zone())
            self.position = new_pos

        if self.position_rept >= 15:
            self.position_rept = 0
            event_callbacks.on_robot_stuck(self.robot_id.name)

        #################   Verifica se chegou ao destino   #################
        if(self.target_position):
            if self.target_position.is_in_range(self.position, self.configuration.threshould_arrived_target):
                print(f"chegou {self.configuration.threshould_arrived_target} -- {self.target_position} -- {self.position}")
                self.target_position = None
                event_callbacks.on_target_reached(self.robot_id.name)

        #TODO CHAMAR FUNÇÃO PARA VERIFICAR VISIBILIDADE BOLA - GOL
        #TODO CHAMAR FUNÇÃO PARA VISIBILIDADE DE PASSE 
        #TODO IMPLEMENTAR MOVIMENTAÇÃO
        #   -> TEMSO QUE ACOMPANHAR O MOVIMENTO DO BOB, MAS O TICK DA ARVORE VAI SER LENTO
        #   -> PODEMOS OU CHAMAR UMA THREAD OU FAZER UM ESQUEMA DE MOVIMENTAÇÃO DENTRO DA UPDATE
        #   -> PODEMOS FAZER ELE SEMPRE SEGUIR O OBJETIVO DELE, EM UMA LISTA DE POS
        #   -> A UPDATE VAI SER CHAMADA TODOS OS CICLOS, ENTÃO PODEMOS USA-LA PARA MOV.

        
        self.velocity = self.world_state.get_team_robot_velocity(self.robot_id.value)

        
    #---------------------------------------------------------------------------------------#
    #                                         Setters                                       #
    #---------------------------------------------------------------------------------------#
    def set_position(self, position: Pose2D):
        """Define manualmente a posição e recalcula quadrante e role."""
        self.position = position
        self.quadrant_index = self.position.get_quadrant()

    def set_velocity(self, velocity: Pose2D):
        """Atualiza o vetor de velocidade (vx, vy)."""
        self.velocity = velocity

    def set_orientation(self, angle: float):
        """Define a orientação atual do robô."""
        self.orientation = angle

    def set_target_position(self, position: Pose2D):
        """Define uma posição alvo (goal) para planejamento de movimento."""
        self.target_position = position

    def reset(self):
        """Restaura o estado para valores padrão (limpa alvo, role e quadrante)."""
        self.position = Pose2D()
        self.velocity = Pose2D()
        self.target_position = Pose2D()
        self.active_function = None
        self.current_command = None
        self.has_ball = False
        self.quadrant_index = None
        self.role = None
        self.setup_callbacks()

    #---------------------------------------------------------------------------------------#
    #                                   METRICAS/CONSULTAS                                  #
    #---------------------------------------------------------------------------------------#
    def check_ball_possession(self) -> bool:
        ball_position = self.world_state.get_ball_position()
        if self.position and ball_position:
            return self.position.distance_to(ball_position) <= BALL_POSSESSION_DISTANCE
        print("ERRO, POS da BOLA OU do ROBO NULOS")
        return False
    # =================== Getters simples para agregador ===================
    def get_position(self)-> Pose2D:
        return self.position

    def get_velocity(self)-> Pose2D:
        return self.velocity
    
    # =================== Internos de classificação ===================
    