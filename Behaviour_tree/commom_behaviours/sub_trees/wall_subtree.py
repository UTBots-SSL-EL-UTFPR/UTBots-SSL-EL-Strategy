# wall subtree.py
import py_trees

import Behaviour_tree.helpers as hp
import Behaviour_tree.commom_behaviours as cb
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.helpers.field_helper import FieldHelper
from Behaviour_tree.core.World_State import World_State

from utils.pose2D import ZoneType, Pose2D

def clamp_out_goalkeeper_area(pos: Pose2D) -> Pose2D:
    """
    Project the position along the goal-to-pos line to just outside the goalkeeper area.
    Assumes the goalkeeper area is a rectangle and ZoneType.TEAM_GOALKEEPER.value.get_bounds() exists.
    """
    gk_zone = ZoneType.TEAM_GOALKEEPER.value  # Zone object

    if not gk_zone.contains(pos.x, pos.y):
        return pos

    # Get the center of our goal
    goal_center = FieldHelper.get_team_goal_center()

    # Direction vector from goal to pos
    dx = pos.x - goal_center.x
    dy = pos.y - goal_center.y
    length = (dx**2 + dy**2) ** 0.5
    if length == 0:
        return pos

    # Get goalkeeper area bounds
    quad = next(iter(gk_zone.quadrants))
    x_min, x_max, y_min, y_max = quad.x_min, quad.x_max, quad.y_min, quad.y_max
    t_candidates = []

    # Avoid division by zero
    if dx != 0:
        t_xmin = (x_min - goal_center.x) / dx
        t_xmax = (x_max - goal_center.x) / dx
        t_candidates.extend([t_xmin, t_xmax])
    if dy != 0:
        t_ymin = (y_min - goal_center.y) / dy
        t_ymax = (y_max - goal_center.y) / dy
        t_candidates.extend([t_ymin, t_ymax])

    # Find intersection points that are inside the rectangle
    intersections = []
    for t in t_candidates:
        if 0 < t < 1:
            x = goal_center.x + dx * t
            y = goal_center.y + dy * t
            if (x_min - 1e-6) <= x <= (x_max + 1e-6) and (y_min - 1e-6) <= y <= (y_max + 1e-6):
                intersections.append((t, x, y))

    if not intersections:
        return pos  # fallback

    # Use the intersection closest to the goal center (smallest t)
    t_exit, x_exit, y_exit = sorted(intersections, key=lambda item: item[0])[0]

    # Step just outside the area (margin)
    margin = 10  # mm
    t_margin = t_exit - margin / length
    x_final = goal_center.x + dx * t_margin
    y_final = goal_center.y + dy * t_margin

    return Pose2D(x_final, y_final, pos.theta)

class PositionOnBallGoalLine(py_trees.behaviour.Behaviour):
    def __init__(self, robot: Bob, name: str = "PositionOnBallGoalLine"):
        super().__init__(name)
        self.robot = robot

    def update(self) -> py_trees.common.Status:
        ws = World_State.get_object()
        ball = ws.get_ball_position()
        if ball is None:
            return py_trees.common.Status.FAILURE

        # Get opponent goal center
        goal_center = FieldHelper.get_team_goal_center()

        # Compute a point on the line ball->goal, at a margin from the ball
        target = Pose2D.align_two(ball, goal_center, margin=200, is_left_team=True)
        # Clamp to stay out of the goalkeeper area
        target = clamp_out_goalkeeper_area(target)

        self.robot.set_new_target(target)
        self.robot.fast_movement()
        return py_trees.common.Status.SUCCESS

def get_wall_subtree(robot: Bob) -> py_trees.composites.Sequence:
    foes_have_ball = cb.condition.FoesHaveBall(robot)
    position_wall_node = PositionOnBallGoalLine(robot)
    move_node = cb.actions.Move_node(robot)
    wall_subtree = py_trees.composites.Sequence(
        "barreira", 
        True,
        children=[foes_have_ball, position_wall_node, move_node],
    )

    wall_root = py_trees.trees.BehaviourTree(wall_subtree)
    wall_root.setup()
    return wall_root
