# defense_helpers.py
# Minimal wall system helpers that reuse existing codebase functionality

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
    """Find and return the goalkeeper robot from the BobManager."""
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
    Return up to `n_wall` robots chosen to form the wall.
    Excludes goalkeeper and any robot that currently has the ball.
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

    # Sort by distance using existing Pose2D.distance_to()
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
    """Determine whether there's a threatening foe and compute the primary foe and its visibility."""
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
        dist_to_ball = ball.distance_to(foe)  # Use existing Pose2D method
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
            dist_to_ball = ball.distance_to(foe)  # Use existing Pose2D method
            if vis_angle > min_vis_angle and dist_to_ball < threat_distance_exit:
                still_threat = True
                break
        new_wall_active = still_threat

    return is_threat, primary_foe, primary_vis, new_wall_active


def choose_wall_size(vis_angle: float, vis_angle_for_2: float = 0.35, 
                    min_vis_angle: float = 0.20, max_wall: int = 2, min_wall: int = 1) -> int:
    """Choose wall size based on visibility angle."""
    if vis_angle >= vis_angle_for_2:
        return min(max_wall, 2)
    if vis_angle >= min_vis_angle:
        return min(max_wall, 1)
    return min_wall


def calculate_unified_wall_parameters(robot_id: int, wall_type: str = "main") -> dict:
    """
    Unified wall parameter calculation for both main and auxiliary walls.
    Uses existing geometry and positioning helpers where possible.
    """
    import py_trees
    from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import (
        WALL_FACTOR, MIN_WALL_DIST, MAX_WALL_DIST
    )
    
    # Setup common variables
    ws = World_State.get_object()
    bb = py_trees.blackboard.Blackboard()
    prefix = f"wall_{robot_id}_"
    
    # Check activation state
    active = getattr(bb, prefix + "active", False)
    primary_foe = getattr(bb, prefix + "primary_foe", None)
    vis_angle = getattr(bb, prefix + "vis_angle", 0.0)
    
    if not active or primary_foe is None:
        return {}
    
    # Common calculations
    goal_center = FieldHelper.get_team_goal_center()
    post_top, post_bottom = FieldHelper.get_team_goal_posts()
    ball = ws.get_ball_position()
    
    # Use existing distance calculation
    foe_to_goal = goal_center.distance_to(primary_foe)
    base_dist = max(MIN_WALL_DIST, min(MAX_WALL_DIST, foe_to_goal * WALL_FACTOR))
    
    # Wall size calculation
    if wall_type == "main":
        n_wall = 1  # Main wall always uses exactly 1 robot
        # Simple positioning along ball->goal line using existing geometry helper
        center_point = GeometryHelper.calculate_point_on_line(ball, goal_center, base_dist)
        center_x, center_y = center_point.x, center_point.y
        
        # Perpendicular direction for wall orientation
        dx = goal_center.x - ball.x
        dy = goal_center.y - ball.y
        length = ball.distance_to(goal_center)
        if length == 0:
            return {}
        ux, uy = dx / length, dy / length
        perp_dx, perp_dy = -uy, ux
        
        offsets = [0.0]  # Single robot at center
        
    else:  # auxiliary wall
        n_wall = max(1, choose_wall_size(vis_angle))
        
        # Choose better side between the two goal posts
        # Use existing distance calculations
        gk_pos = _get_goalkeeper_position_or_fallback()
        
        dist_top = gk_pos.distance_to(post_top)
        dist_bottom = gk_pos.distance_to(post_bottom)
        chosen_post = post_top if dist_top >= dist_bottom else post_bottom
        
        # Position toward the chosen post using existing geometry helper
        center_point = GeometryHelper.calculate_point_on_line(ball, chosen_post, base_dist)
        center_x, center_y = center_point.x, center_point.y
        
        # Perpendicular direction
        dx = chosen_post.x - ball.x
        dy = chosen_post.y - ball.y
        length = ball.distance_to(chosen_post)
        if length == 0:
            return {}
        ux, uy = dx / length, dy / length
        perp_dx, perp_dy = -uy, ux
        
        # Multiple robots spread along perpendicular
        if n_wall == 1:
            offsets = [0.0]
        else:
            spacing = 2 * ROBOT_RADIUS + 20
            total_span = (n_wall - 1) * spacing
            offsets = [i * spacing - total_span/2 for i in range(n_wall)]
    
    # Robot selection using existing functionality
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
    """Get goalkeeper position or fallback to goal center."""
    gk_bob = find_goalkeeper()
    if gk_bob and hasattr(gk_bob, 'state') and gk_bob.state:
        gk_pos = getattr(gk_bob.state, 'position', None)
        if gk_pos:
            return gk_pos
    return FieldHelper.get_team_goal_center()


def apply_wall_positioning_constraints(target: Pose2D, ball: Pose2D) -> Pose2D:
    """
    Apply simple positioning constraints to keep wall robots in valid positions.
    """
    # Simple field boundary check using field helper
    from Behaviour_tree.helpers.field_helper import HALF_LEGHT
    
    # Clamp to field boundaries with margin
    margin = 100
    constrained_x = max(-HALF_LEGHT + margin, min(target.x, HALF_LEGHT - margin))
    constrained_y = max(-HALF_LEGHT + margin, min(target.y, HALF_LEGHT - margin))
    constrained = Pose2D(constrained_x, constrained_y, target.theta)
    
    # Simple goalkeeper area avoidance
    gk_zone = ZoneType.TEAM_GOALKEEPER.value
    if gk_zone.contains(constrained.x, constrained.y):
        # Push away from goal center
        goal_center = FieldHelper.get_team_goal_center()
        dx = constrained.x - goal_center.x
        dy = constrained.y - goal_center.y
        length = goal_center.distance_to(constrained)
        
        if length > 0:
            # Push further out by 150mm margin
            safety_margin = 150
            scale_factor = (length + safety_margin) / length
            constrained.x = goal_center.x + dx * scale_factor
            constrained.y = goal_center.y + dy * scale_factor
    
    return constrained


def clamp_out_goalkeeper_area(pos: Pose2D) -> Pose2D:
    """
    Simple wrapper that projects position out of goalkeeper area.
    """
    return apply_wall_positioning_constraints(pos, pos)
