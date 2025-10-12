# wall subtree.py

# -------------------------------------------------------------------------- #
#                                  IMPORTS                                   #
# -------------------------------------------------------------------------- #
import py_trees
import math
from typing import List, Optional, Any

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.core.World_State import World_State

from utils.defines import ROBOT_RADIUS
from utils.pose2D import ZoneType, Pose2D, Zone, Quadrant, RoleType
from Behaviour_tree.helpers.visiblidade_gol import max_range_of_visibility
from Behaviour_tree.commom_behaviours import actions as cb_actions, condition as cb_condition

# -------------------------------------------------------------------------- #
#                           CONSTANTES E CONFIGURAÇÃO                          #
# -------------------------------------------------------------------------- #


THREAT_DISTANCE_ENTER = 1200.0  # mm: quando entra na "zona de ameaça"
THREAT_DISTANCE_EXIT = 1400.0   # mm: quando sai na "zona de ameaça"
MIN_VIS_ANGLE = 0.20            # rad: a visibilidade mínima do gol para ser considerado uma ameaça
MIN_WALL = 1                    
MAX_WALL = 2
VIS_ANGLE_FOR_2 = 0.35
WALL_FACTOR = 0.25              # fração da distância do oponente->gol para posicionar a parede
MIN_WALL_DIST = 200.0
MAX_WALL_DIST = 1000.0

 # -------------------------------------------------------------------------- #
#                           CFUNÇOES AUXILIARES                        #
# -------------------------------------------------------------------------- #


def get_bounds_of_zone(zone: Zone) -> Optional[tuple]:
    """
    Return (x_min, x_max, y_min, y_max) of the zone if available, else None.
    """
    x_min, x_max, y_min, y_max = None, None, None, None
    quadrants = zone.quadrants

    for quadrant in quadrants:
        if x_min is None or quadrant.x_min < x_min:
            x_min = quadrant.x_min
        if x_max is None or quadrant.x_max > x_max:
            x_max = quadrant.x_max
        if y_min is None or quadrant.y_min < y_min:
            y_min = quadrant.y_min
        if y_max is None or quadrant.y_max > y_max:
            y_max = quadrant.y_max
    return (x_min, x_max, y_min, y_max)

def clamp_out_goalkeeper_area(pos):
    """
    Project the position along the goal-to-pos line to just outside the goalkeeper area.
    Assumes the goalkeeper area is a rectangle and ZoneType.TEAM_GOALKEEPER.value.get_bounds() exists.
    """

    gk_zone = ZoneType.TEAM_GOALKEEPER.value 

    if not gk_zone.contains(pos.x, pos.y):
        return pos

    goal_center = FieldHelper.get_team_goal_center()

    dx = pos.x - goal_center.x
    dy = pos.y - goal_center.y
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return pos

    x_min, x_max, y_min, y_max = get_bounds_of_zone(gk_zone)
    if x_min is None:
        return pos  
    t_candidates = []

    if dx != 0:
        t_xmin = (x_min - goal_center.x) / dx
        t_xmax = (x_max - goal_center.x) / dx
        t_candidates.extend([t_xmin, t_xmax])
    if dy != 0:
        t_ymin = (y_min - goal_center.y) / dy
        t_ymax = (y_max - goal_center.y) / dy
        t_candidates.extend([t_ymin, t_ymax])

    intersections = []
    for t in t_candidates:
        if 0 < t < 1:
            x = goal_center.x + dx * t
            y = goal_center.y + dy * t
            if (x_min - 1e-6) <= x <= (x_max + 1e-6) and (y_min - 1e-6) <= y <= (y_max + 1e-6):
                intersections.append((t, x, y))

    if not intersections:
        return pos  

    t_exit = (sorted(intersections, key=lambda item: item[0])[0])[0]

    
    margin = 10
    t_outside = t_exit + margin / length
    x_final = goal_center.x + dx * t_outside
    y_final = goal_center.y + dy * t_outside

    return Pose2D(x_final, y_final, getattr(pos, 'theta', 0))

def get_wall_robots(center_point: Optional[Any] = None, n_wall: Optional[int] = None) -> List[Bob]:
    """
    Return up to `n_wall` robots chosen to form the wall.
    Uses BobManager to access Bob instances (which hold Bob_State with has_ball and role).
    Excludes goalkeeper and any robot that currently has the ball.
    Selection is deterministic: sort by distance to center_point, tie-break on robot_id.value.
    """

    bob_mgr = BobManager.get_object()
    all_bobs = list(bob_mgr.bobs.values())

    candidates: List[Bob] = []
    for b in all_bobs:
        if b is None or not hasattr(b, 'state') or b.state is None:
            continue
        if getattr(b.state, 'role', None) == RoleType.GOALKEEPER:
            continue
        candidates.append(b)

    if n_wall is None or center_point is None:
        return candidates

    entries = [] 
    for r in candidates:
        pos = getattr(r.state, 'position', None)
        if pos is None:
            pos = Pose2D(0, 0, 0)
        dist = math.hypot(pos.x - center_point.x, pos.y - center_point.y)
        rid = getattr(r, 'robot_id', None)
        tie = rid.value if rid is not None else 0
        entries.append((r, dist, tie))

    entries.sort(key=lambda e: (e[1], e[2]))
    selected = [e[0] for e in entries[: max(0, min(n_wall, len(entries)) )]]
    return selected

def is_robot_outside_gk_area(robot: Bob) -> bool:
    """
    Returns True if the robot's full body is outside the goalkeeper area.
    """
    gk_zone = ZoneType.TEAM_GOALKEEPER.value
    
    pos = robot.get_position() if hasattr(robot, 'get_position') else robot.pose
    
    x_min, x_max, y_min, y_max = get_bounds_of_zone(gk_zone)
    if x_min is not None:
        if (pos.x + ROBOT_RADIUS < x_min or pos.x - ROBOT_RADIUS > x_max or
            pos.y + ROBOT_RADIUS < y_min or pos.y - ROBOT_RADIUS > y_max):
            return True
        return False
    return not gk_zone.contains(pos.x, pos.y)

def is_threatening_foe(ws: World_State, gk_zone : Zone, ball, goal_center, prev_wall_active: bool = False, threat_distance_enter=THREAT_DISTANCE_ENTER, threat_distance_exit=THREAT_DISTANCE_EXIT, min_vis_angle=MIN_VIS_ANGLE):
    """
    Stateless helper: determine whether there's a threatening foe and compute the "primary" foe and its visibility.
    Uses `prev_wall_active` only to select which distance threshold to apply (hysteresis), but does NOT modify any global state.

    Returns: (is_threat: bool, primary_foe: Optional[Pose2D], vis_angle: float, new_wall_active: bool)
    """
    foes = ws.get_all_foes_position()
    obstacles = ws.get_all_team_position() + ws.get_all_foes_position()

    threshold = threat_distance_exit if prev_wall_active else threat_distance_enter

    primary_foe = None
    primary_vis = 0.0
    primary_dist = float('inf')

    for foe in foes:
        if gk_zone.contains(foe.x, foe.y):
            continue
        vis_angle = max_range_of_visibility(obstacles, foe, goal_center.x)
        dist_to_ball = math.hypot(foe.x - ball.x, foe.y - ball.y)
        if vis_angle > min_vis_angle and dist_to_ball < threshold:
            if dist_to_ball < primary_dist:
                primary_dist = dist_to_ball
                primary_foe = foe
                primary_vis = vis_angle

    is_threat = primary_foe is not None

    if is_threat:
        new_wall_active = True
    else:
        still_threat = False
        for foe in foes:
            if gk_zone.contains(foe.x, foe.y):
                continue
            vis_angle = max_range_of_visibility(obstacles, foe, goal_center.x)
            dist_to_ball = math.hypot(foe.x - ball.x, foe.y - ball.y)
            if vis_angle > min_vis_angle and dist_to_ball < threat_distance_exit:
                still_threat = True
                break
        new_wall_active = still_threat

    return is_threat, primary_foe, primary_vis, new_wall_active

def choose_wall_size(vis_angle: float) -> int:
    if (vis_angle >= VIS_ANGLE_FOR_2):
        return min(MAX_WALL, 2)
    if (vis_angle >= MIN_VIS_ANGLE):
        return min(MAX_WALL, 1)
    return MIN_WALL


# +------------------------------------------------------------------------+ #
# |                         DEFINIÇÃO DE CONDIÇÕES                             | #
# +------------------------------------------------------------------------+ #

class IsRobotOutsideGKArea(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "IsRobotOutsideGKArea"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        if is_robot_outside_gk_area(self.robot):
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsThreateningFoe(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "IsThreateningFoe", threat_distance=1200, min_vis_angle=0.2):
        super().__init__(name)
        self.robot = robot
        self.threat_distance = threat_distance
        self.min_vis_angle = min_vis_angle

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        gk_zone = ZoneType.TEAM_GOALKEEPER.value
        ball = ws.get_ball_position()
        goal_center = FieldHelper.get_team_goal_center()

        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"
        prev_active = getattr(bb, prefix + "active", False)

        is_threat, primary_foe, vis, new_active = is_threatening_foe(
            ws,
            gk_zone,
            ball,
            goal_center,
            prev_wall_active=prev_active,
            threat_distance_enter=self.threat_distance,
            threat_distance_exit=THREAT_DISTANCE_EXIT,
            min_vis_angle=self.min_vis_angle,
        )

        setattr(bb, prefix + "active", new_active)

        if new_active and primary_foe is not None:
            setattr(bb, prefix + "primary_foe", primary_foe)
            setattr(bb, prefix + "vis_angle", vis)
        else:

            if hasattr(bb, prefix + "primary_foe"):
                delattr(bb, prefix + "primary_foe")
            if hasattr(bb, prefix + "vis_angle"):
                delattr(bb, prefix + "vis_angle")

        if is_threat:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE    


class IsRobotAssignedToWall(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "IsRobotAssignedToWall"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        selected_ids = getattr(bb, prefix + "selected_ids", None)
        if selected_ids is None:
            return py_trees.common.Status.FAILURE

        if getattr(self.robot, 'robot_id', None) in selected_ids:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


# +------------------------------------------------------------------------+ #
# |                         DEFINIÇÃO DE AÇÕES                             | #
# +------------------------------------------------------------------------+ #

class CalculateWallParameters(py_trees.behaviour.Behaviour):
    """Compute wall center, size and which robots should form the wall. Write results to the blackboard.

    This node centralizes the repeated calculations so other nodes only read results from the blackboard.
    """
    def __init__(self, robot: Bob, name: str = "CalculateWallParameters"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        active = getattr(bb, prefix + "active", False)
        primary_foe = getattr(bb, prefix + "primary_foe", None)
        vis_angle = getattr(bb, prefix + "vis_angle", 0.0)

        if not active or primary_foe is None:
            for k in ("center_x", "center_y", "perp_dx", "perp_dy", "spacing", "n_wall", "selected_ids"):
                if hasattr(bb, prefix + k):
                    delattr(bb, prefix + k)
            return py_trees.common.Status.FAILURE

        n_wall = choose_wall_size(vis_angle)

        goal_center = FieldHelper.get_team_goal_center()
        foe_to_goal = math.hypot(primary_foe.x - goal_center.x, primary_foe.y - goal_center.y)
        center_dist = max(MIN_WALL_DIST, min(MAX_WALL_DIST, foe_to_goal * WALL_FACTOR))

        ball = ws.get_ball_position()
        dx = goal_center.x - ball.x
        dy = goal_center.y - ball.y
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            return py_trees.common.Status.FAILURE
        perp_dx = -dy / length
        perp_dy = dx / length

        center_x = ball.x + dx / length * center_dist
        center_y = ball.y + dy / length * center_dist

        center_point = Pose2D(center_x, center_y, 0)

        spacing = 2 * ROBOT_RADIUS + 20
        selected = get_wall_robots(center_point=center_point, n_wall=n_wall)
        selected_ids = [getattr(r, 'robot_id', None) for r in selected]

        setattr(bb, prefix + "center_x", center_x)
        setattr(bb, prefix + "center_y", center_y)
        setattr(bb, prefix + "perp_dx", perp_dx)
        setattr(bb, prefix + "perp_dy", perp_dy)
        setattr(bb, prefix + "spacing", spacing)
        setattr(bb, prefix + "n_wall", n_wall)
        setattr(bb, prefix + "selected_ids", selected_ids)

        return py_trees.common.Status.SUCCESS
class PositionOnBallGoalLine(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "PositionOnBallGoalLine"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{self.robot.robot_id}_"

        center_x = getattr(bb, prefix + "center_x", None)
        center_y = getattr(bb, prefix + "center_y", None)
        perp_dx = getattr(bb, prefix + "perp_dx", None)
        perp_dy = getattr(bb, prefix + "perp_dy", None)
        spacing = getattr(bb, prefix + "spacing", None)
        selected_ids = getattr(bb, prefix + "selected_ids", None)

        if None in (center_x, center_y, perp_dx, perp_dy, spacing, selected_ids):
            return py_trees.common.Status.FAILURE

        my_id = getattr(self.robot, 'robot_id', None)
        if my_id not in selected_ids:
            return py_trees.common.Status.FAILURE

        idx = selected_ids.index(my_id)
        offset = (idx - (len(selected_ids) - 1) / 2) * spacing
        target_x = center_x + perp_dx * offset
        target_y = center_y + perp_dy * offset
        target = Pose2D(target_x, target_y, 0)

        target = clamp_out_goalkeeper_area(target)

        self.robot.set_new_target(target)
        self.robot.fast_movement()
        return py_trees.common.Status.SUCCESS

# =========================================================================== #
# ====================== CRIAÇÃO DA ÁRVORE DE BARREIRA ====================== #
# =========================================================================== #


def get_wall_subtree(robot: Bob) -> py_trees.composites.Sequence:

    foes_have_ball = cb_condition.FoesHaveBall(robot)
    is_threatening_foe = IsThreateningFoe(robot)

    calculate_params = CalculateWallParameters(robot)

    is_assigned = IsRobotAssignedToWall(robot)
    is_outside_gk = IsRobotOutsideGKArea(robot)

    position_wall_node = PositionOnBallGoalLine(robot)
    move_node = cb_actions.Move_node(robot)

    wall_sequence = py_trees.composites.Sequence(
        "Form Wall Sequence",
        memory=True, 
        children=[
            foes_have_ball,
            is_threatening_foe,
            calculate_params,
            is_assigned,
            is_outside_gk,
            position_wall_node,
            move_node,
        ],
    )
    wall_root = py_trees.trees.BehaviourTree(wall_sequence)
    wall_root.setup()
    return wall_root
