from utils import defines
from utils.defines import ZoneType, RoleType, QuadrantType, Quadrant
from utils.pose2D import Pose2D

from ..core.World_State import World_State,RobotID

from SSL_configuration.configuration import Configuration

from typing import Iterable 

GOALKEEPER_DISTANCE_X = 2250
HALF_GOALKEEPER_AREA_WIDTH = 675
GOAL_LENGHT = 500

WALL_MARGIN = 200
KEEPER_MARGIN = 200
INFLUENCE_RADIUS = 500   
GRID_STEP = 250  

HALF_LEGHT = int(4500 / 2)
HALF_WID = int(3000 / 2)


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
            max(0, dist_to_top_border)
        )
    @staticmethod
    def verify_quadrant_free(quad: Quadrant, max_dist_from_border: int) -> bool:
        all_robots: list[Pose2D]
        all_robots = Positioning_helper._world_state.get_all_robot_position()

        robots_in_quad = [position for position in all_robots if position.quadrant.name == quad.name] # type: ignore

        if not robots_in_quad:
            return True
        return all(
            Positioning_helper.distance_to_quadrant_border(robot, quad) <= max_dist_from_border
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
        y_in_range = (-HALF_GOALKEEPER_AREA_WIDTH - margin < pose.y < HALF_GOALKEEPER_AREA_WIDTH + margin)
        if not y_in_range:
            return False
        x_abs = abs(pose.x)
        x_in_range = (GOALKEEPER_DISTANCE_X - GOAL_LENGHT - margin < x_abs < GOALKEEPER_DISTANCE_X + margin)
        return x_in_range
    
    @staticmethod
    def outside_walls(pose: Pose2D, margin):
        return (abs(pose.x) > 2250 - margin or abs(pose.y) > 1500 - margin)
    
    @staticmethod
    def outside_enemies_influence(pose: Pose2D) -> bool:
        foes = Positioning_helper._world_state.get_all_foes_position()
        for e in foes:
            if pose.distance_to(e) < INFLUENCE_RADIUS:
                return False
        return True