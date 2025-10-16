# defense_helpers.py

import math
from typing import List, Optional, Any, Tuple

from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.bob_manager import BobManager
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.core.World_State import World_State

from utils.defines import ROBOT_RADIUS
from utils.pose2D import ZoneType, Pose2D, Zone, RoleType


def get_bounds_of_zone(zone: Zone) -> Optional[Tuple[float, float, float, float]]:
    """
    Return (x_min, x_max, y_min, y_max) of the zone if available, else None.
    
    Args:
        zone: Zone object to get bounds for
        
    Returns:
        Tuple of (x_min, x_max, y_min, y_max) or None if unavailable
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


def clamp_out_goalkeeper_area(pos: Pose2D) -> Pose2D:
    """
    Project the position along the goal-to-pos line to just outside the goalkeeper area.
    
    Args:
        pos: Position to clamp out of goalkeeper area
        
    Returns:
        Position outside goalkeeper area with safety margin
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

    bounds = get_bounds_of_zone(gk_zone)
    if bounds is None:
        return pos
    
    x_min, x_max, y_min, y_max = bounds
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


def find_goalkeeper() -> Optional[Bob]:
    """
    Find and return the goalkeeper robot from the BobManager.
    
    Returns:
        Bob instance with GOALKEEPER role, or None if not found
    """
    bob_mgr = BobManager.get_object()
    
    for bob in bob_mgr.bobs.values():
        if (bob and 
            hasattr(bob, 'state') and 
            bob.state is not None and 
            getattr(bob.state, 'role', None) == RoleType.GOALKEEPER):
            return bob
    
    return None


def get_goalkeeper_position() -> Optional[Pose2D]:
    """
    Get the current position of the goalkeeper.
    
    Returns:
        Goalkeeper position or None if goalkeeper not found or has no position
    """
    gk_bob = find_goalkeeper()
    if gk_bob is None:
        return None
    
    return getattr(gk_bob.state, 'position', None)


def get_wall_robots(center_point: Optional[Pose2D] = None, n_wall: Optional[int] = None) -> List[Bob]:
    """
    Return up to `n_wall` robots chosen to form the wall.
    Uses BobManager to access Bob instances.
    Excludes goalkeeper and any robot that currently has the ball.
    Selection is deterministic: sort by distance to center_point, tie-break on robot_id.value.
    
    Args:
        center_point: Position to sort robots by distance from
        n_wall: Maximum number of robots to select
        
    Returns:
        List of Bob instances suitable for wall formation
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
        dist = math.hypot(pos.x - center_point.x, pos.y - center_point.y)
        robot_id = getattr(robot, 'robot_id', None)
        tie = robot_id.value if robot_id is not None else 0
        entries.append((robot, dist, tie))

    entries.sort(key=lambda e: (e[1], e[2]))
    selected = [e[0] for e in entries[:max(0, min(n_wall, len(entries)))]]
    return selected


def is_robot_outside_gk_area(robot: Bob) -> bool:
    """
    Returns True if the robot's full body is outside the goalkeeper area.
    
    Args:
        robot: Robot to check
        
    Returns:
        True if robot is completely outside goalkeeper area
    """
    gk_zone = ZoneType.TEAM_GOALKEEPER.value

    pos = robot.state.get_position() if hasattr(robot, 'state') else robot.pose

    bounds = get_bounds_of_zone(gk_zone)
    if bounds is not None:
        x_min, x_max, y_min, y_max = bounds
        if (pos.x + ROBOT_RADIUS < x_min or pos.x - ROBOT_RADIUS > x_max or
            pos.y + ROBOT_RADIUS < y_min or pos.y - ROBOT_RADIUS > y_max):
            return True
        return False
    
    return not gk_zone.contains(pos.x, pos.y)


def get_farthest_goal_post_from_goalkeeper() -> Pose2D:
    """
    Determine which goal post is farthest from the goalkeeper position.
    
    Returns:
        The goal post farthest from goalkeeper, or top post if no goalkeeper found
    """
    post_top, post_bottom = FieldHelper.get_team_goal_posts()
    gk_pos = get_goalkeeper_position()
    
    if gk_pos is None:
        return post_top  # Fallback to top post
    
    dist_top = math.hypot(post_top.x - gk_pos.x, post_top.y - gk_pos.y)
    dist_bottom = math.hypot(post_bottom.x - gk_pos.x, post_bottom.y - gk_pos.y)
    
    return post_top if dist_top >= dist_bottom else post_bottom


def calculate_triangle_area(p1: Pose2D, p2: Pose2D, p3: Pose2D) -> float:
    """
    Calculate triangle area using cross product.
    
    Args:
        p1, p2, p3: Triangle vertices
        
    Returns:
        Area of the triangle
    """
    return 0.5 * abs((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y))


def apply_field_boundary_constraints(target: Pose2D, margin: float = 50) -> Pose2D:
    """
    Apply field boundary constraints with specified margin.
    
    Args:
        target: Target position to constrain
        margin: Safety margin from field boundaries
        
    Returns:
        Constrained position within field boundaries
    """
    from Behaviour_tree.helpers.field_helper import HALF_LEGHT
    
    constrained_x = max(-HALF_LEGHT + margin, min(target.x, HALF_LEGHT - margin))
    constrained_y = max(-HALF_LEGHT + margin, min(target.y, HALF_LEGHT - margin))
    
    return Pose2D(constrained_x, constrained_y, target.theta)


def can_block_triangle_side(ball_pos: Pose2D, gk_pos: Pose2D, post_pos: Pose2D, 
                           potential_wall_pos: Pose2D) -> bool:
    """
    Calculate if wall position creates effective blocking angle within a triangle.
    
    Determines if a potential wall position can effectively block the triangle formed
    by ball, goalkeeper, and goal post by checking cross products to verify positioning.
    
    Args:
        ball_pos: Ball position (triangle vertex)
        gk_pos: Goalkeeper position (triangle vertex)
        post_pos: Goal post position (triangle vertex)
        potential_wall_pos: Potential wall position to evaluate
        
    Returns:
        True if wall position creates effective blocking within the triangle
    """
    ball_to_wall_x = potential_wall_pos.x - ball_pos.x
    ball_to_wall_y = potential_wall_pos.y - ball_pos.y
    ball_to_post_x = post_pos.x - ball_pos.x
    ball_to_post_y = post_pos.y - ball_pos.y
    ball_to_gk_x = gk_pos.x - ball_pos.x
    ball_to_gk_y = gk_pos.y - ball_pos.y
    
    # Cross products to determine positioning relative to triangle edges
    cross_wall_post = ball_to_wall_x * ball_to_post_y - ball_to_wall_y * ball_to_post_x
    cross_wall_gk = ball_to_wall_x * ball_to_gk_y - ball_to_wall_y * ball_to_gk_x
    cross_post_gk = ball_to_post_x * ball_to_gk_y - ball_to_post_y * ball_to_gk_x
    
    # Wall should be between ball->post and ball->gk directions for effective blocking
    if cross_post_gk != 0:
        same_side_post = (cross_wall_post * cross_post_gk) > 0
        same_side_gk = (cross_wall_gk * cross_post_gk) < 0
        return same_side_post and same_side_gk
    
    return False


def calculate_blocking_effectiveness_score(triangle_area: float, distance_efficiency: float,
                                         angle_to_goal: float) -> float:
    """
    Calculate blocking effectiveness score for wall positioning.
    
    Combines triangle coverage area, distance efficiency, and angle optimization
    to determine the overall effectiveness of a wall position.
    
    Args:
        triangle_area: Area of the triangle being blocked
        distance_efficiency: Ratio of base distance to actual distance
        angle_to_goal: Angle from wall position to goal for optimization
        
    Returns:
        Effectiveness score (higher is better)
    """
    # Base score from coverage area and distance efficiency
    coverage_score = triangle_area * distance_efficiency
    
    # Bonus for positions that maintain good defensive angles
    angle_bonus = 1.0 + 0.2 * math.cos(angle_to_goal)
    
    return coverage_score * angle_bonus


def calculate_adaptive_wall_distance(ball: Pose2D, goal_center: Pose2D, base_distance: float,
                                     threat_level: float = 1.0, wall_type: str = "main", 
                                     visibility_angle: float = 0.0) -> float:
    """
    Calculate adaptive wall distance using goalkeeper-inspired depth factor logic.
    
    Args:
        ball: Ball position
        goal_center: Center of our goal
        base_distance: Base distance calculation from threat analysis
        threat_level: Threat level multiplier (e.g., visibility angle factor)
        wall_type: Type of wall ("main" or "auxiliary") for different depth factors
        visibility_angle: Visibility angle for high-threat adjustment
        
    Returns:
        Optimized wall distance considering ball proximity and threat level
    """
    # Distance from ball to our goal (similar to goalkeeper logic)
    dist_ball_to_goal = math.hypot(ball.x - goal_center.x, ball.y - goal_center.y)
    
    # Adaptive depth factor based on ball proximity and wall type
    if wall_type == "auxiliary":
        # Auxiliary wall uses slightly more aggressive positioning
        if dist_ball_to_goal < 600:
            depth_factor = 0.3  # Close ball - position closer for immediate blocking
        elif dist_ball_to_goal < 1200:
            depth_factor = 0.5  # Medium distance - balanced positioning
        elif dist_ball_to_goal < 2500:
            depth_factor = 0.7  # Far ball - optimize for area coverage
        else:
            depth_factor = 0.9  # Very far ball - maximize coverage potential
    else:
        # Main wall uses more conservative positioning
        if dist_ball_to_goal < 500:
            depth_factor = 0.2  # Very close ball - wall stays closer to ball
        elif dist_ball_to_goal < 1000:
            depth_factor = 0.4  # Medium distance - balanced positioning
        elif dist_ball_to_goal < 2000:
            depth_factor = 0.6  # Far ball - positioned further for area coverage
        else:
            depth_factor = 0.8  # Very far ball - maximize coverage area
    
    # Apply depth factor and threat level adjustments
    adaptive_distance = base_distance * depth_factor * threat_level
    
    # Additional adjustment based on visibility angle (high visibility = closer positioning)
    # This helps with immediate threat response similar to goalkeeper pressure situations
    if visibility_angle > 0.35:  # High visibility threat (VIS_ANGLE_FOR_2 threshold)
        adaptive_distance *= 0.8  # Move closer for better blocking
    
    # Ensure distance stays within reasonable bounds
    from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import MIN_WALL_DIST, MAX_WALL_DIST
    return max(MIN_WALL_DIST, min(MAX_WALL_DIST, adaptive_distance))


def evaluate_side_blocking_effectiveness(ball: Pose2D, gk_pos: Pose2D, post: Pose2D, 
                                       base_dist: float, robot_id: int = None) -> tuple:
    """
    Evaluate the blocking effectiveness of positioning wall toward a specific goal post.
    
    Args:
        ball: Ball position
        gk_pos: Goalkeeper position
        post: Goal post position to evaluate
        base_dist: Base distance for wall positioning
        robot_id: Robot ID for blackboard access (optional)
        
    Returns:
        (best_score, best_center_x, best_center_y, best_perp_dx, best_perp_dy, triangle_area)
    """
    from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import VIS_ANGLE_FOR_2, MIN_WALL_DIST, MAX_WALL_DIST
    from utils.pose2D import ZoneType
    import py_trees
    
    area = calculate_triangle_area(ball, gk_pos, post)
    best_score = 0
    best_center_x = ball.x
    best_center_y = ball.y
    best_perp_dx = 1
    best_perp_dy = 0
    
    # Get visibility angle for adaptive distance calculation
    vis_angle = 0.0
    if robot_id is not None:
        bb = py_trees.blackboard.Blackboard()
        prefix = f"wall_{robot_id}_"
        vis_angle = getattr(bb, prefix + "vis_angle", 0.0)
    
    # Test multiple distances with goalkeeper-style depth optimization
    adaptive_base = calculate_adaptive_wall_distance(ball, post, base_dist, 
                                                   wall_type="auxiliary", 
                                                   visibility_angle=vis_angle)
    test_distances = [adaptive_base * 0.75, adaptive_base, adaptive_base * 1.25]
    
    for test_dist in test_distances:
        # Direction from ball toward post
        dx = post.x - ball.x
        dy = post.y - ball.y
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            test_center_x = ball.x + ux * test_dist
            test_center_y = ball.y + uy * test_dist
            test_pos = Pose2D(test_center_x, test_center_y, 0)
            
            # Enhanced constraint checking (goalkeeper-style area avoidance)
            gk_zone = ZoneType.TEAM_GOALKEEPER.value
            if not gk_zone.contains(test_center_x, test_center_y):
                # Apply additional field boundary constraints
                field_margin = 100
                test_constrained = apply_field_boundary_constraints(
                    Pose2D(test_center_x, test_center_y, 0), field_margin)
                within_field = (test_constrained.x == test_center_x and 
                              test_constrained.y == test_center_y)
                
                if within_field and can_block_triangle_side(ball, gk_pos, post, test_pos):
                    # Enhanced scoring with distance efficiency and coverage area
                    distance_efficiency = adaptive_base / test_dist
                    
                    # Angle optimization for defensive positioning
                    angle_to_goal = math.atan2(test_center_y - post.y, test_center_x - post.x)
                    
                    # Use shared helper for effectiveness scoring
                    total_score = calculate_blocking_effectiveness_score(
                        area, distance_efficiency, angle_to_goal)
                    
                    if total_score > best_score:
                        best_score = total_score
                        best_center_x = test_center_x
                        best_center_y = test_center_y
                        best_perp_dx = -uy
                        best_perp_dy = ux
    
    return best_score, best_center_x, best_center_y, best_perp_dx, best_perp_dy, area


def apply_enhanced_positioning_constraints(target: Pose2D, ball: Pose2D, 
                                         goal_center: Pose2D) -> Pose2D:
    """
    Apply comprehensive positioning constraints using goalkeeper-inspired logic.
    
    Args:
        target: Initial target position
        ball: Current ball position
        goal_center: Center of the goal being defended
        
    Returns:
        Constrained position optimized for auxiliary wall effectiveness
    """
    from utils.pose2D import ZoneType
    
    # Step 1: Field boundary constraints with adaptive margins
    # Distance-based field margin (closer ball = more conservative margins)
    ball_distance = math.hypot(ball.x - goal_center.x, ball.y - goal_center.y)
    if ball_distance < 1000:
        field_margin = 80  # Conservative for close threats
    elif ball_distance < 2000:
        field_margin = 60  # Balanced margins
    else:
        field_margin = 40  # Aggressive for distant threats
    
    constrained_target = apply_field_boundary_constraints(target, field_margin)
    
    # Step 2: Enhanced goalkeeper area avoidance with directional projection
    gk_zone = ZoneType.TEAM_GOALKEEPER.value
    if gk_zone.contains(constrained_target.x, constrained_target.y):
        # Project position away from goal using ball direction as guidance
        ball_to_target_x = constrained_target.x - ball.x
        ball_to_target_y = constrained_target.y - ball.y
        projection_length = math.hypot(ball_to_target_x, ball_to_target_y)
        
        if projection_length > 0:
            # Normalize and extend beyond GK area
            norm_x = ball_to_target_x / projection_length
            norm_y = ball_to_target_y / projection_length
            
            # Calculate minimum distance to exit GK area
            bounds = get_bounds_of_zone(gk_zone)
            
            if bounds is not None:
                x_min, x_max, y_min, y_max = bounds
                # Project to edge of GK area plus safety margin
                safety_margin = 120  # Larger margin for auxiliary walls
                
                # Find intersection point with GK area boundary
                edge_distance = 0
                if norm_x > 0:
                    edge_distance = max(edge_distance, (x_max - ball.x) / norm_x)
                elif norm_x < 0:
                    edge_distance = max(edge_distance, (x_min - ball.x) / norm_x)
                
                if norm_y > 0:
                    edge_distance = max(edge_distance, (y_max - ball.y) / norm_y)
                elif norm_y < 0:
                    edge_distance = max(edge_distance, (y_min - ball.y) / norm_y)
                
                # Position beyond GK area
                safe_distance = edge_distance + safety_margin
                constrained_target.x = ball.x + norm_x * safe_distance
                constrained_target.y = ball.y + norm_y * safe_distance
    
    # Step 3: Triangle coverage optimization (maintain blocking effectiveness)
    # Ensure final position still maintains good blocking angle
    target_to_goal_x = goal_center.x - constrained_target.x
    target_to_goal_y = goal_center.y - constrained_target.y
    target_to_ball_x = ball.x - constrained_target.x  
    target_to_ball_y = ball.y - constrained_target.y
    
    # Check if position maintains reasonable blocking angle
    dot_product = (target_to_goal_x * target_to_ball_x + 
                  target_to_goal_y * target_to_ball_y)
    goal_distance = math.hypot(target_to_goal_x, target_to_goal_y)
    ball_distance = math.hypot(target_to_ball_x, target_to_ball_y)
    
    if goal_distance > 0 and ball_distance > 0:
        cos_angle = dot_product / (goal_distance * ball_distance)
        blocking_angle = math.acos(max(-1, min(1, cos_angle)))
        
        # If blocking angle is too wide, adjust position slightly toward ball
        if blocking_angle > math.pi * 0.6:  # More than 108 degrees
            adjustment_factor = 0.15
            constrained_target.x += (ball.x - constrained_target.x) * adjustment_factor
            constrained_target.y += (ball.y - constrained_target.y) * adjustment_factor
    
    return constrained_target


def analyze_threatening_foe(ws: World_State, gk_zone: Zone, ball, goal_center, prev_wall_active: bool = False, 
                           threat_distance_enter: float = 1200.0, threat_distance_exit: float = 1400.0, 
                           min_vis_angle: float = 0.20):
    """
    Stateless helper: determine whether there's a threatening foe and compute the "primary" foe and its visibility.
    Uses `prev_wall_active` only to select which distance threshold to apply (hysteresis), but does NOT modify any global state.

    Args:
        ws: World_State object
        gk_zone: Goalkeeper zone for exclusion checks
        ball: Ball position
        goal_center: Goal center position
        prev_wall_active: Previous wall activation state for hysteresis
        threat_distance_enter: Distance threshold for entering threat mode
        threat_distance_exit: Distance threshold for exiting threat mode
        min_vis_angle: Minimum visibility angle to be considered a threat

    Returns: 
        (is_threat: bool, primary_foe: Optional[Pose2D], vis_angle: float, new_wall_active: bool)
    """
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


def choose_wall_size(vis_angle: float, vis_angle_for_2: float = 0.35, 
                    min_vis_angle: float = 0.20, max_wall: int = 2, min_wall: int = 1) -> int:
    """
    Choose wall size based on visibility angle.
    
    Args:
        vis_angle: Current visibility angle
        vis_angle_for_2: Threshold for 2-robot wall
        min_vis_angle: Minimum visibility angle for wall
        max_wall: Maximum wall size
        min_wall: Minimum wall size
        
    Returns:
        Number of robots for the wall
    """
    if vis_angle >= vis_angle_for_2:
        return min(max_wall, 2)
    if vis_angle >= min_vis_angle:
        return min(max_wall, 1)
    return min_wall


def apply_wall_positioning_constraints(target: Pose2D, ball: Pose2D) -> Pose2D:
    """
    Apply goalkeeper-style positioning constraints including area avoidance and field boundaries.
    
    Args:
        target: Initial target position
        ball: Current ball position for constraint calculations
        
    Returns:
        Constrained position that respects field boundaries and avoids goalkeeper area
    """
    from Behaviour_tree.helpers.field_helper import FieldHelper
    from utils.pose2D import ZoneType
    
    # Step 1: Apply field boundary constraints (similar to goalkeeper area clamping)
    field_margin = 50  # Keep robots away from walls
    constrained_target = apply_field_boundary_constraints(target, field_margin)
    
    # Step 2: Apply goalkeeper area avoidance (enhanced version of clamp_out_goalkeeper_area)
    constrained_target = clamp_out_goalkeeper_area(constrained_target)
    
    # Step 3: Additional safety margin from critical areas
    gk_zone = ZoneType.TEAM_GOALKEEPER.value
    if gk_zone.contains(constrained_target.x, constrained_target.y):
        # If still in GK area after clamping, project further out along ball->target direction
        goal_center = FieldHelper.get_team_goal_center()
        dx = constrained_target.x - goal_center.x
        dy = constrained_target.y - goal_center.y
        length = math.hypot(dx, dy)
        
        if length > 0:
            # Move target further from goal by additional safety margin
            safety_margin = 100  # mm
            scale_factor = (length + safety_margin) / length
            constrained_target.x = goal_center.x + dx * scale_factor
            constrained_target.y = goal_center.y + dy * scale_factor
    
    return constrained_target


# ===================== GEOMETRIC INTERPOLATION & INTERSECTION UTILITIES =====================

def calculate_angle_bisector(point_origin: Pose2D, point1: Pose2D, point2: Pose2D) -> tuple:
    """
    Calculate the angle bisector direction from origin between two points.
    
    Args:
        point_origin: Origin point (e.g., ball position)
        point1: First direction point (e.g., goalkeeper)
        point2: Second direction point (e.g., goal post)
        
    Returns:
        (bisector_x, bisector_y, angle_width): Normalized bisector direction and angle width
    """
    # Vectors from origin to each point
    vec1_x = point1.x - point_origin.x
    vec1_y = point1.y - point_origin.y
    vec2_x = point2.x - point_origin.x
    vec2_y = point2.y - point_origin.y
    
    # Normalize vectors
    len1 = math.hypot(vec1_x, vec1_y)
    len2 = math.hypot(vec2_x, vec2_y)
    
    if len1 == 0 or len2 == 0:
        return 0, 0, 0
    
    unit1_x, unit1_y = vec1_x / len1, vec1_y / len1
    unit2_x, unit2_y = vec2_x / len2, vec2_y / len2
    
    # Calculate bisector direction (average of unit vectors)
    bisector_x = (unit1_x + unit2_x) / 2
    bisector_y = (unit1_y + unit2_y) / 2
    bisector_len = math.hypot(bisector_x, bisector_y)
    
    if bisector_len == 0:
        return 0, 0, 0
        
    # Normalize bisector
    bisector_x /= bisector_len
    bisector_y /= bisector_len
    
    # Calculate angle width between the two directions
    dot_product = unit1_x * unit2_x + unit1_y * unit2_y
    angle_width = math.acos(max(-1, min(1, dot_product)))
    
    return bisector_x, bisector_y, angle_width


def interpolate_position_along_line(start: Pose2D, end: Pose2D, distance: float) -> Pose2D:
    """
    Interpolate a position along a line at a specific distance from start.
    
    Args:
        start: Starting point
        end: Ending point (defines direction)
        distance: Distance from start point
        
    Returns:
        Interpolated position
    """
    dx = end.x - start.x
    dy = end.y - start.y
    length = math.hypot(dx, dy)
    
    if length == 0:
        return start
    
    # Unit direction vector
    ux, uy = dx / length, dy / length
    
    # Calculate interpolated position
    new_x = start.x + ux * distance
    new_y = start.y + uy * distance
    
    return Pose2D(new_x, new_y, 0)


def find_line_intersection(line1_start: Pose2D, line1_end: Pose2D, 
                          line2_start: Pose2D, line2_end: Pose2D) -> Pose2D:
    """
    Find intersection point between two lines.
    
    Args:
        line1_start, line1_end: First line definition
        line2_start, line2_end: Second line definition
        
    Returns:
        Intersection point, or None if lines are parallel
    """
    # Line 1: (x1,y1) to (x2,y2)
    x1, y1 = line1_start.x, line1_start.y
    x2, y2 = line1_end.x, line1_end.y
    
    # Line 2: (x3,y3) to (x4,y4)  
    x3, y3 = line2_start.x, line2_start.y
    x4, y4 = line2_end.x, line2_end.y
    
    # Calculate intersection using determinants
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    
    if abs(denom) < 1e-10:  # Lines are parallel
        return None
    
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    
    # Calculate intersection point
    ix = x1 + t * (x2 - x1)
    iy = y1 + t * (y2 - y1)
    
    return Pose2D(ix, iy, 0)


def project_point_onto_line(point: Pose2D, line_start: Pose2D, line_end: Pose2D) -> tuple:
    """
    Project a point onto a line and return the projection point and distance along line.
    
    Args:
        point: Point to project
        line_start: Start of line
        line_end: End of line
        
    Returns:
        (projected_point, distance_along_line, perpendicular_distance)
    """
    # Vector along the line
    line_dx = line_end.x - line_start.x
    line_dy = line_end.y - line_start.y
    line_length_sq = line_dx * line_dx + line_dy * line_dy
    
    if line_length_sq == 0:
        return line_start, 0, math.hypot(point.x - line_start.x, point.y - line_start.y)
    
    # Vector from line start to point
    point_dx = point.x - line_start.x
    point_dy = point.y - line_start.y
    
    # Project point onto line (dot product)
    projection_factor = (point_dx * line_dx + point_dy * line_dy) / line_length_sq
    
    # Calculate projected point
    proj_x = line_start.x + projection_factor * line_dx
    proj_y = line_start.y + projection_factor * line_dy
    projected_point = Pose2D(proj_x, proj_y, 0)
    
    # Distance along line
    distance_along_line = projection_factor * math.sqrt(line_length_sq)
    
    # Perpendicular distance from point to line
    perp_distance = math.hypot(point.x - proj_x, point.y - proj_y)
    
    return projected_point, distance_along_line, perp_distance


def calculate_optimal_blocking_position(ball: Pose2D, target_point: Pose2D, 
                                       blocking_distance: float, 
                                       constraint_points: list = None) -> Pose2D:
    """
    Calculate optimal blocking position between ball and target using geometric interpolation.
    
    Args:
        ball: Ball position
        target_point: Point to block (e.g., goal center or post)
        blocking_distance: Distance from ball to position blocker
        constraint_points: Optional list of points to avoid (e.g., goalkeeper position)
        
    Returns:
        Optimal blocking position
    """
    # Basic position along ball->target line
    basic_position = interpolate_position_along_line(ball, target_point, blocking_distance)
    
    # If no constraints, return basic position
    if not constraint_points:
        return basic_position
    
    # Adjust position to avoid constraint points
    adjusted_position = basic_position
    
    for constraint in constraint_points:
        distance_to_constraint = math.hypot(
            adjusted_position.x - constraint.x,
            adjusted_position.y - constraint.y
        )
        
        # If too close to constraint, push position away
        min_clearance = 200  # mm
        if distance_to_constraint < min_clearance:
            # Calculate direction away from constraint
            away_x = adjusted_position.x - constraint.x
            away_y = adjusted_position.y - constraint.y
            away_length = math.hypot(away_x, away_y)
            
            if away_length > 0:
                # Push to minimum clearance
                scale = min_clearance / away_length
                adjusted_position.x = constraint.x + away_x * scale
                adjusted_position.y = constraint.y + away_y * scale
    
    return adjusted_position


def calculate_side_preference_offset(center_point: Pose2D, perpendicular_direction: tuple,
                                   threat_point: Pose2D, goal_posts: tuple, 
                                   wall_width: float) -> float:
    """
    Calculate which side of the center line to prefer for auxiliary wall positioning.
    
    Args:
        center_point: Center point of the wall line
        perpendicular_direction: (perp_dx, perp_dy) perpendicular to wall line
        threat_point: Threatening opponent position
        goal_posts: (post_left, post_right) goal post positions
        wall_width: Total width available for wall
        
    Returns:
        Offset along perpendicular direction (positive/negative indicates preferred side)
    """
    perp_dx, perp_dy = perpendicular_direction
    post_left, post_right = goal_posts
    
    # Project posts onto perpendicular line
    offset_left = ((post_left.x - center_point.x) * perp_dx + 
                   (post_left.y - center_point.y) * perp_dy)
    offset_right = ((post_right.x - center_point.x) * perp_dx + 
                    (post_right.y - center_point.y) * perp_dy)
    
    left_o, right_o = min(offset_left, offset_right), max(offset_left, offset_right)
    mid_o = 0.5 * (left_o + right_o)
    
    # Project threat point onto perpendicular line
    threat_offset = ((threat_point.x - center_point.x) * perp_dx + 
                     (threat_point.y - center_point.y) * perp_dy)
    
    # Choose side based on threat location
    if threat_offset >= mid_o:
        # Threat on right side, position wall on right
        preferred_offset = 0.5 * (mid_o + right_o)
    else:
        # Threat on left side, position wall on left
        preferred_offset = 0.5 * (left_o + mid_o)
    
    return preferred_offset


def calculate_unified_wall_parameters(robot_id: int, wall_type: str = "main") -> dict:
    """
    Unified wall parameter calculation for both main and auxiliary walls.
    
    Args:
        robot_id: ID of the robot requesting wall parameters
        wall_type: "main" for main wall, "aux" for auxiliary wall
        
    Returns:
        Dictionary containing all calculated wall parameters, or empty dict if invalid
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
        return {}  # Return empty dict to indicate failure
    
    # Common calculations
    goal_center = FieldHelper.get_team_goal_center()
    post_top, post_bottom = FieldHelper.get_team_goal_posts()
    ball = ws.get_ball_position()
    
    # Goalkeeper detection and positioning
    gk_bob = find_goalkeeper()
    chosen_post = get_farthest_goal_post_from_goalkeeper()
    gk_pos = get_goalkeeper_position()
    if gk_pos is None:
        gk_pos = goal_center
    
    # Base distance calculation (same for both wall types)
    foe_to_goal = math.hypot(primary_foe.x - goal_center.x, primary_foe.y - goal_center.y)
    base_dist = max(MIN_WALL_DIST, min(MAX_WALL_DIST, foe_to_goal * WALL_FACTOR))
    
    # Wall size calculation
    if wall_type == "main":
        n_wall = 1  # Main wall always uses exactly 1 robot
    else:  # auxiliary wall
        n_wall = max(1, choose_wall_size(vis_angle))
    
    # Strategy-specific positioning calculations
    if wall_type == "main":
        # Main wall uses bisector strategy
        result = _calculate_main_wall_position(ball, gk_pos, chosen_post, goal_center, 
                                              primary_foe, base_dist, vis_angle, robot_id)
    else:
        # Auxiliary wall uses side evaluation strategy  
        result = _calculate_aux_wall_position(ball, gk_pos, post_top, post_bottom, 
                                            goal_center, primary_foe, base_dist, robot_id)
    
    if not result:
        return {}
    
    # Add common parameters
    result.update({
        'n_wall': n_wall,
        'spacing': 2 * ROBOT_RADIUS + 20,
        'vis_angle': vis_angle,
        'base_dist': base_dist
    })
    
    return result


def _calculate_main_wall_position(ball, gk_pos, chosen_post, goal_center, 
                                 base_dist, vis_angle) -> dict:
    """Calculate position parameters for main wall (bisector strategy)."""
    from Behaviour_tree.commom_behaviours.sub_trees.wall_subtree import MIN_WALL_DIST, MAX_WALL_DIST
    
    gk_bob = find_goalkeeper()
    
    if gk_bob is None:
        # Simple ball->post positioning
        dx = chosen_post.x - ball.x
        dy = chosen_post.y - ball.y
        length = math.hypot(dx, dy)
        if length == 0:
            return {}
            
        center_dist = calculate_adaptive_wall_distance(
            ball, goal_center, base_dist, wall_type="main", visibility_angle=vis_angle
        )
        ux, uy = dx / length, dy / length
        center_x = ball.x + ux * center_dist
        center_y = ball.y + uy * center_dist
        perp_dx, perp_dy = -uy, ux
    else:
        # Bisector-based positioning
        bisector_x, bisector_y, angle_width = calculate_angle_bisector(ball, gk_pos, chosen_post)
        if bisector_x == 0 and bisector_y == 0:
            return {}
            
        # Distance adjustment based on angle width
        angle_factor = 1.0 + (angle_width / math.pi)
        center_dist = max(MIN_WALL_DIST, min(MAX_WALL_DIST, base_dist * angle_factor))
        
        # Position using optimal blocking calculation
        center_point = calculate_optimal_blocking_position(
            ball, goal_center, center_dist, constraint_points=[gk_pos]
        )
        center_x, center_y = center_point.x, center_point.y
        perp_dx, perp_dy = -bisector_y, bisector_x
    
    # Single robot positioned at center
    offsets = [0.0]
    
    # Robot selection
    selected = get_wall_robots(center_point=Pose2D(center_x, center_y, 0), n_wall=1)
    selected_ids = [getattr(r, 'robot_id', None) for r in selected]
    
    return {
        'center_x': center_x,
        'center_y': center_y, 
        'perp_dx': perp_dx,
        'perp_dy': perp_dy,
        'selected_ids': selected_ids,
        'offsets': offsets
    }


def _calculate_aux_wall_position(ball, gk_pos, post_top, post_bottom, 
                               primary_foe, base_dist, robot_id) -> dict:
    """Calculate position parameters for auxiliary wall (side evaluation strategy)."""
    
    # Evaluate both sides using enhanced effectiveness analysis
    top_score, top_center_x, top_center_y, top_perp_dx, top_perp_dy, top_area = \
        evaluate_side_blocking_effectiveness(ball, gk_pos, post_top, base_dist, robot_id)
    
    bottom_score, bottom_center_x, bottom_center_y, bottom_perp_dx, bottom_perp_dy, bottom_area = \
        evaluate_side_blocking_effectiveness(ball, gk_pos, post_bottom, base_dist, robot_id)
    
    # Choose the side with better blocking effectiveness
    if top_score > bottom_score:
        best_center_x, best_center_y = top_center_x, top_center_y
        best_perp_dx, best_perp_dy = top_perp_dx, top_perp_dy
    elif bottom_score > 0:
        best_center_x, best_center_y = bottom_center_x, bottom_center_y
        best_perp_dx, best_perp_dy = bottom_perp_dx, bottom_perp_dy
    else:
        # Fallback positioning
        gk_bob = find_goalkeeper()
        if gk_bob is not None:
            dist_top = math.hypot(post_top.x - gk_pos.x, post_top.y - gk_pos.y)
            dist_bottom = math.hypot(post_bottom.x - gk_pos.x, post_bottom.y - gk_pos.y)
            chosen_post = post_top if dist_top >= dist_bottom else post_bottom
        else:
            chosen_post = post_top
            
        fallback_position = interpolate_position_along_line(ball, chosen_post, base_dist)
        best_center_x, best_center_y = fallback_position.x, fallback_position.y
        
        # Calculate perpendicular direction
        dx = chosen_post.x - ball.x
        dy = chosen_post.y - ball.y
        length = math.hypot(dx, dy)
        if length == 0:
            return {}
        ux, uy = dx / length, dy / length
        best_perp_dx, best_perp_dy = -uy, ux
    
    center_x, center_y = best_center_x, best_center_y
    perp_dx, perp_dy = best_perp_dx, best_perp_dy
    
    # Side selection logic for auxiliary wall
    post_left, post_right = FieldHelper.get_team_goal_posts()
    offset_left = (post_left.x - center_x) * perp_dx + (post_left.y - center_y) * perp_dy
    offset_right = (post_right.x - center_x) * perp_dx + (post_right.y - center_y) * perp_dy
    left_o, right_o = min(offset_left, offset_right), max(offset_left, offset_right)
    mid_o = 0.5 * (left_o + right_o)
    
    # Calculate threat offset for side selection
    foe_offset = (primary_foe.x - center_x) * perp_dx + (primary_foe.y - center_y) * perp_dy
    if foe_offset >= mid_o:
        side_start, side_end = mid_o, right_o
    else:
        side_start, side_end = left_o, mid_o
    
    # Get wall size for offset calculation
    n_wall = max(1, choose_wall_size(getattr(get_blackboard(), f"wall_{robot_id}_vis_angle", 0.0)))
    
    # Build offsets within chosen side span
    if n_wall == 1:
        offsets = [0.5 * (side_start + side_end)]
    else:
        span = side_end - side_start
        offsets = [side_start + (span * i) / max(1, n_wall - 1) for i in range(n_wall)]
    
    # Robot selection
    side_center_offset = 0.5 * (side_start + side_end)
    center_point = Pose2D(center_x + perp_dx * side_center_offset, 
                         center_y + perp_dy * side_center_offset, 0)
    selected = get_wall_robots(center_point=center_point, n_wall=n_wall)
    selected_ids = [getattr(r, 'robot_id', None) for r in selected]
    
    return {
        'center_x': center_x,
        'center_y': center_y,
        'perp_dx': perp_dx, 
        'perp_dy': perp_dy,
        'selected_ids': selected_ids,
        'offsets': offsets
    }


def get_blackboard():
    """Helper to get blackboard instance."""
    import py_trees
    return py_trees.blackboard.Blackboard()
