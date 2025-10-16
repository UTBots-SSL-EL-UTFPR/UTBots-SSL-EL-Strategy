# defense_helpers.py

import math
from typing import List, Optional

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.helpers.geometry_helper import GeometryHelper
from Behaviour_tree.core.World_State import World_State

from utils.defines import ROBOT_RADIUS
from utils.pose2D import ZoneType, Pose2D, RoleType, Zone


def find_goalkeeper() -> Optional[Bob]:
    """Acha o goleiro"""
    bob_mgr = BobManager.get_object()
    
    for bob in bob_mgr.bobs.values():
        if (bob and 
            hasattr(bob, 'state') and 
            bob.state is not None and 
            getattr(bob.state, 'role', None) == RoleType.GOALKEEPER):
            return bob
    
    return None


def get_wall_robots(center_point: Optional[Pose2D] = None, n_wall: Optional[int] = None) -> List[Bob]:
    """
    Retorna os robos da barreira
    """
    bob_mgr = BobManager.get_object()
    all_bobs = list(bob_mgr.bobs.values())

    candidates: List[Bob] = []
    for bob in all_bobs:
        if bob is None or not hasattr(bob, 'state') or bob.state is None:
            continue
        if getattr(bob.state, 'role', None) == RoleType.GOALKEEPER:
            continue
        candidates.append(bob)

    if n_wall is None or center_point is None:
        return candidates

    entries = [] 
    for robot in candidates:
        pos = getattr(robot.state, 'position', None)
        if pos is None:
            pos = Pose2D(0, 0, 0)
        dist = center_point.distance_to(pos)
        robot_id = getattr(robot, 'robot_id', None)
        tie = robot_id.value if robot_id is not None else 0
        entries.append((robot, dist, tie))

    entries.sort(key=lambda e: (e[1], e[2]))
    selected = [e[0] for e in entries[:max(0, min(n_wall, len(entries)))]]
    return selected


def analyze_threatening_foe(ws: World_State, gk_zone: Zone, ball, goal_center, prev_wall_active: bool = False, 
                           threat_distance_enter: float = 1200.0, threat_distance_exit: float = 1400.0, 
                           min_vis_angle: float = 0.20):
    """Verifica ameaças, o adversário mais perigoso e seu angulo de visão"""
    from Behaviour_tree.helpers.visiblidade_gol import max_range_of_visibility
    
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
        dist_to_ball = ball.distance_to(foe)  
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
            dist_to_ball = ball.distance_to(foe)  
            if vis_angle > min_vis_angle and dist_to_ball < threat_distance_exit:
                still_threat = True
                break
        new_wall_active = still_threat

    return is_threat, primary_foe, primary_vis, new_wall_active


def choose_wall_size(vis_angle: float, vis_angle_for_2: float = 0.35, 
                    min_vis_angle: float = 0.20, max_wall: int = 2, min_wall: int = 1) -> int:
    """Escolha do tamanho da barreira"""
    if vis_angle >= vis_angle_for_2:
        return min(max_wall, 2)
    if vis_angle >= min_vis_angle:
        return min(max_wall, 1)
    return min_wall


def calculate_unified_wall_parameters(robot_id: int, wall_type: str = "main") -> dict:
    """
    Calcula os parâmetros utilizados por ambos barreira e auxiliar.
    """
    import py_trees
    from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import (
        WALL_FACTOR, MIN_WALL_DIST, MAX_WALL_DIST
    )
    
    
    ws = World_State.get_object()
    bb = py_trees.blackboard.Blackboard()
    prefix = f"wall_{robot_id}_"
    
    
    active = getattr(bb, prefix + "active", False)
    primary_foe = getattr(bb, prefix + "primary_foe", None)
    vis_angle = getattr(bb, prefix + "vis_angle", 0.0)
    
    if not active or primary_foe is None:
        return {}
    
   
    goal_center = FieldHelper.get_team_goal_center()
    post_top, post_bottom = FieldHelper.get_team_goal_posts()
    ball = ws.get_ball_position()
    
    
    foe_to_goal = goal_center.distance_to(primary_foe)
    base_dist = max(MIN_WALL_DIST, min(MAX_WALL_DIST, foe_to_goal * WALL_FACTOR))
    
    
    if wall_type == "main":
        n_wall = 1  
        
        
        gk_pos = _get_goalkeeper_position_or_fallback()
        
        
        dist_top = gk_pos.distance_to(post_top)
        dist_bottom = gk_pos.distance_to(post_bottom)
        farthest_post = post_top if dist_top >= dist_bottom else post_bottom
        
    
        bisector_dir = GeometryHelper.calculate_bisector_direction(
            ball, gk_pos, farthest_post
        )
        
       
        center_point = GeometryHelper.calculate_point_on_line(
            ball, 
            Pose2D(ball.x + bisector_dir.x * 1000, ball.y + bisector_dir.y * 1000, 0),
            base_dist
        )
        
        center_point = apply_wall_positioning_constraints(center_point, ball)
        center_x, center_y = center_point.x, center_point.y
        
    
        perp_dx, perp_dy = -bisector_dir.y, bisector_dir.x
        
        offsets = [0.0]  
        
    else:  # auxiliary wall
        n_wall = max(1, choose_wall_size(vis_angle))
        
        
        gk_pos = _get_goalkeeper_position_or_fallback()
        gk_zone = ZoneType.TEAM_GOALKEEPER.value
        
        
        best_position = None
        best_coverage_angle = 0.0
        
        
        candidates = []
        for angle_offset in [-45, -30, -15, 0, 15, 30, 45]:  
            angle = math.atan2(goal_center.y - ball.y, goal_center.x - ball.x) + math.radians(angle_offset)
            for dist_factor in [0.8, 1.0, 1.2]: 
                dist = base_dist * dist_factor
                candidate_x = ball.x + dist * math.cos(angle)
                candidate_y = ball.y + dist * math.sin(angle)
                candidate = Pose2D(candidate_x, candidate_y, 0)
                
                
                if gk_zone.contains(candidate.x, candidate.y):
                    continue
                    
                candidates.append(candidate)
        
        for candidate in candidates:
            angle_to_top = math.atan2(post_top.y - candidate.y, post_top.x - candidate.x)
            angle_to_bottom = math.atan2(post_bottom.y - candidate.y, post_bottom.x - candidate.x)
            
            coverage = abs(angle_to_top - angle_to_bottom)
            
            gk_dist_factor = min(1.0, candidate.distance_to(gk_pos) / 500.0)
            weighted_coverage = coverage * gk_dist_factor
            
            if weighted_coverage > best_coverage_angle:
                best_coverage_angle = weighted_coverage
                best_position = candidate
        
        if best_position is None:
            best_position = GeometryHelper.calculate_point_on_line(ball, goal_center, base_dist)

        best_position = apply_wall_positioning_constraints(best_position, ball)
        center_x, center_y = best_position.x, best_position.y
        center_point = best_position

        dx = goal_center.x - ball.x
        dy = goal_center.y - ball.y
        length = ball.distance_to(goal_center)
        if length == 0:
            return {}
        ux, uy = dx / length, dy / length
        perp_dx, perp_dy = -uy, ux
        
        if n_wall == 1:
            offsets = [0.0]
        else:
            spacing = 2 * ROBOT_RADIUS + 20
            total_span = (n_wall - 1) * spacing
            offsets = [i * spacing - total_span/2 for i in range(n_wall)]
    
    selected = get_wall_robots(center_point=Pose2D(center_x, center_y, 0), n_wall=n_wall)
    selected_ids = [getattr(r, 'robot_id', None) for r in selected]
    
    return {
        'center_x': center_x,
        'center_y': center_y, 
        'perp_dx': perp_dx,
        'perp_dy': perp_dy,
        'spacing': 2 * ROBOT_RADIUS + 20,
        'n_wall': n_wall,
        'selected_ids': selected_ids,
        'offsets': offsets,
        'vis_angle': vis_angle,
        'base_dist': base_dist
    }


def _get_goalkeeper_position_or_fallback() -> Pose2D:
    """Pega a posição do goleiro"""
    gk_bob = find_goalkeeper()
    if gk_bob and hasattr(gk_bob, 'state') and gk_bob.state:
        gk_pos = getattr(gk_bob.state, 'position', None)
        if gk_pos:
            return gk_pos
    return FieldHelper.get_team_goal_center()


def apply_wall_positioning_constraints(target: Pose2D, ball: Pose2D) -> Pose2D:
    """
    Usado para manter a barreira em áreas válidas
    """
    
    from Behaviour_tree.helpers.field_helper import HALF_LEGHT

    margin = 100
    constrained_x = max(-HALF_LEGHT + margin, min(target.x, HALF_LEGHT - margin))
    constrained_y = max(-HALF_LEGHT + margin, min(target.y, HALF_LEGHT - margin))
    constrained = Pose2D(constrained_x, constrained_y, target.theta)
    
    
    gk_zone = ZoneType.TEAM_GOALKEEPER.value
    if gk_zone.contains(constrained.x, constrained.y):
        
        goal_center = FieldHelper.get_team_goal_center()
        dx = constrained.x - goal_center.x
        dy = constrained.y - goal_center.y
        length = goal_center.distance_to(constrained)
        
        if length > 0:
            
            safety_margin = 150
            scale_factor = (length + safety_margin) / length
            constrained.x = goal_center.x + dx * scale_factor
            constrained.y = goal_center.y + dy * scale_factor
    
    return constrained
