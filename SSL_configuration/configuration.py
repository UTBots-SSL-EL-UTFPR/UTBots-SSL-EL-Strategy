import json
from datetime import datetime


class Configuration:
    """Fiz meio de sacanagem, pois este nao faz muito sentido pensando em enviar os comando pelo terminal.
    Mesmo assim este sera util pois facilita o codigo, e eu estava pensando melhor quanto a cascar os
    parametros via terminal, nao sera nada eficiente e escalavel, desse jeito fica mais facil realizar
    varios testes em sequencia."""

    _instance = None

    def __init__(self):
        self.is_left_team = None
        self.foes_id = []

        self.vision = None
        self.referee = None

        self.interface_ip_referee = None
        self.interface_ip_vision = None

        self.vision_receiver_ip = None
        self.referee_receiver_ip = None

        self.team_collor = None
        self.team_robot_1 = None
        self.team_robot_2 = None
        self.team_robot_3 = None

        self.foes_collor = None
        self.foe_robot_1 = None
        self.foe_robot_2 = None
        self.foe_robot_3 = None

        self.goal_position_x = None
        self.goal_position_y = None

        self.suport_dist_from_ball = None
        self.min_wall_margin = None
        self.min_goal_area_margin = None
        self.other_robos_margin = None
        self.max_ball_y_to_goalkeeper_kick = None

        self.threshould_arrived_target = None
        self.distance_to_press_opponent = None

        self.startWithBall = None

    def get_side_sign(self):
        if self.is_left_team:
            return 1
        return -1

    @staticmethod
    def loadFromJson():
        with open("SSL_configuration/configuration.json", "r") as file:
            data = json.load(file)
        return data

    @staticmethod
    def getObject():
        if Configuration._instance is None:
            Configuration._instance = Configuration()
            data = Configuration.loadFromJson()

            instance = Configuration._instance

            instance.is_left_team = data["global"]["is_left_team"]
            instance.foes_id = data["global"]["foes_id"]

            instance.vision = data["Communication"]["Receive"]["Ports"]["vision"]
            instance.referee = data["Communication"]["Receive"]["Ports"]["referee"]

            instance.interface_ip_referee = data["Communication"]["Receive"][
                "IP_Addrs"
            ]["interface_ip_referee"]
            instance.interface_ip_vision = data["Communication"]["Receive"]["IP_Addrs"][
                "interface_ip_vision"
            ]

            instance.vision_receiver_ip = data["Communication"]["Receive"]["IP_Addrs"][
                "vision_receiver_ip"
            ]
            instance.referee_receiver_ip = data["Communication"]["Receive"]["IP_Addrs"][
                "referee_receiver_ip"
            ]

            instance.team_collor = data["Robots"]["team"]["collor"]
            instance.team_robot_1 = data["Robots"]["team"]["robot_id_1"]
            instance.team_robot_2 = data["Robots"]["team"]["robot_id_2"]
            instance.team_robot_3 = data["Robots"]["team"]["robot_id_3"]

            instance.foes_collor = data["Robots"]["foes"]["collor"]
            instance.foe_robot_1 = data["Robots"]["foes"]["robot_id_1"]
            instance.foe_robot_2 = data["Robots"]["foes"]["robot_id_2"]
            instance.foe_robot_3 = data["Robots"]["foes"]["robot_id_3"]

            instance.goal_position_x = data["Positioning"]["goal_center_x"]
            instance.goal_position_y = data["Positioning"]["goal_center_y"]

            instance.suport_dist_from_ball = data["Positioning"]["free_kick"][
                "suport_dist_from_ball"
            ]
            instance.min_wall_margin = data["Positioning"]["free_kick"][
                "min_wall_margin"
            ]
            instance.min_goal_area_margin = data["Positioning"]["free_kick"][
                "min_goal_area_margin"
            ]
            instance.other_robos_margin = data["Positioning"]["free_kick"][
                "other_robos_margin"
            ]
            instance.max_ball_y_to_goalkeeper_kick = data["Positioning"]["free_kick"][
                "max_ball_y_to_goalkeeper_kick"
            ]  # 1m do gol

            instance.threshould_arrived_target = data["Motion"][
                "threshould_arrived_target"
            ]
            instance.startWithBall = data["startWithBall"]

        return Configuration._instance
