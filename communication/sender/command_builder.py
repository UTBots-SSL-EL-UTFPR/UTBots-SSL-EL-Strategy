from communication.generated import grSim_Packet_pb2
from SSL_configuration.configuration import Configuration
import time

class CommandBuilder:
    def __init__(self):
        self.packet = grSim_Packet_pb2.grSim_Packet()   # type: ignore
        conf = Configuration.getObject()
        self.packet.commands.isteamyellow = (conf.team_collor == "yellow")

    def command_robots(
                self, id: int, vx: float = 0.0, vy: float = 0.0, w: float = 0.0,
                kick_x: float = 0.0, kick_z: float = 0.0,
                spinner: bool = False, wheelsspeed: bool = False,
                wheel1: float = 0.0, wheel2: float = 0.0,
                wheel3: float = 0.0, wheel4: float = 0.0):
        
        cmd = self.packet.commands.robot_commands.add() # adiciona um comando de robô
        
        cmd.id          = id
        cmd.velnormal   = vy
        cmd.veltangent  = vx
        cmd.velangular  = w
        cmd.kickspeedx  = kick_x
        cmd.kickspeedz  = kick_z         #são todos os campos de grSim_Commands_pb2.py
        cmd.spinner     = spinner
        cmd.wheelsspeed = wheelsspeed
        cmd.wheel1      = wheel1
        cmd.wheel2      = wheel2
        cmd.wheel3      = wheel3
        cmd.wheel4      = wheel4  

    def replace_robots(self, x: float, y: float, dir: float, id: int, yellowTeam: bool, turnon: bool):
        
        cmd = self.packet.replacement.robots.add() # adiciona um comando de reposicionamento para o robo

        cmd.x           = x
        cmd.y           = y
        cmd.dir         = dir
        cmd.id          = id            #são todos os campos de grSim_Replacement_pb2.py
        cmd.yellowteam  = yellowTeam
        cmd.turnon      = turnon

    def replace_ball(self, x: float, y: float, vx: float, vy: float):
        
        cmd = self.packet.replacement.ball # adiciona um comando de reposicionamento para a bola

        cmd.x   = x
        cmd.y   = y
        cmd.vx  = vx                    #são todos os campos de grSim_Replacement_pb2.py
        cmd.vy  = vy


    def build(self) -> bytes:
        self.packet.commands.timestamp = time.time()    # preenche o campo obrigatório 'timestamp'
        return self.packet.SerializeToString()


'''
TODOS OS COMANDOS POSSIVEIS PARA OS ROBOS NO GRSIM

id	        uint32	ID do robô 
kickspeedx	float	Velocidade do chute reto (X)
kickspeedz	float	Velocidade do chip kick (Z)
veltangent	float	Velocidade tangencial (eixo frente-trás do robô)
velnormal	float	Velocidade normal (eixo lateral do robô)
velangular	float	Velocidade angular (giro do robô)
spinner	    bool	Se o dribbler deve estar ligado
wheelsspeed	bool	Se os campos wheel1 a wheel4 serão usados diretamente
wheel1-4	float	Velocidade individual de cada roda (caso wheelsspeed = True)

TODOS OS COMANDOS POSSIVEIS DE REPOSICIONAMENTO DOS ROBOS

x	        double	Posição X do robô
y	        double	Posição Y do robô
dir	        double	Direção/orientação (em radianos)
id	        uint32	ID do robô
yellowteam	bool	Se é do time amarelo (True) ou azul (False)
turnon	    bool	(opcional) Liga o robô ao colocá-lo na posição

TODOS OS COMANDOS POSSIVEIS DE REPOSICIONAMENTO DA BOLA

x	double	Posição X da bola
y	double	Posição Y da bola
vx	double	Velocidade X inicial da bola
vy	double	Velocidade Y inicial da bola
'''