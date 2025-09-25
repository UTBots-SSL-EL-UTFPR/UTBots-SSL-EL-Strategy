from Behaviour_tree.behaviors.common import actions, condition
from typing import Callable, Tuple, Optional
from utils.pose2D import Pose2D
import py_trees
from Behaviour_tree.robot.bob import Bob
from Behaviour_tree.core.blackboard import Blackboard_Manager

class InterceptBallBehavior(py_trees.composites.Selector):
    """
    Behavior tree for ball interception and defensive actions:
      1. Dispute loose ball (highest priority)
      2. Pressurer actions (constructive tackle, emergency clearance)
      3. Coverage actions (intercept pass, contain, block, emergency clearance, maintain formation)
      4. Strategic positioning
    """

    def __init__(
        self,
        name: str,
        bob : Bob,
        max_radius: int = 700,
    ):
        super().__init__(name=name, memory=True)
        self._bb = Blackboard_Manager.get_instance()
        self.bob = bob
        self.max_radius = max_radius

        # 1. Dispute loose ball
        dispute_loose_ball = py_trees.composites.Sequence(
            name="DisputeLooseBall", memory=True, children=[
                cond_ball_loose_factory(),
                cond_closest_to_ball_factory(),
                communicate_loose_ball_factory(),
                move_factory_to_ball(),
                take_possession_factory(),
            ]
        )

        # 2. Pressurer actions
        pressurer_actions = py_trees.composites.Selector(
            name="PressurerActions", memory=True, children=[
                py_trees.composites.Sequence(
                    name="ConstructiveTackle", memory=True, children=[
                        cond_is_pressurer_factory(),
                        cond_not_in_panic_zone_factory(),
                        contain_opponent_factory(),
                        attempt_tackle_factory(),
                    ]
                ),
                py_trees.composites.Sequence(
                    name="EmergencyClearance", memory=True, children=[
                        cond_is_pressurer_factory(),
                        cond_in_panic_zone_factory(),
                        clear_ball_factory(),
                    ]
                ),
            ]
        )

        # 3. Coverage actions
        coverage_actions = py_trees.composites.Selector(
            name="CoverageActions", memory=True, children=[
                py_trees.composites.Sequence(
                    name="InterceptPass", memory=True, children=[
                        cond_is_coverage_factory(),
                        cond_pass_in_progress_factory(),
                        cond_intercept_time_better_factory(),
                        move_to_intercept_factory(),
                    ]
                ),
                py_trees.composites.Sequence(
                    name="ContainOpponent", memory=True, children=[
                        cond_is_coverage_factory(),
                        cond_opponent_in_zone_factory(),
                        cond_pressurer_needs_help_factory(),
                        approach_to_contain_factory(),
                    ]
                ),
                py_trees.composites.Sequence(
                    name="BlockDangerousAdversary", memory=True, children=[
                        cond_is_coverage_factory(),
                        cond_dangerous_adversary_free_factory(),
                        block_pass_line_factory(),
                    ]
                ),
                py_trees.composites.Sequence(
                    name="CoverageEmergencyClearance", memory=True, children=[
                        cond_is_coverage_factory(),
                        cond_last_defender_factory(),
                        cond_opponent_advancing_factory(),
                        clear_ball_factory(),
                    ]
                ),
                py_trees.behaviours.Success(name="MaintainFormation"),
            ]
        )

        # 4. Strategic positioning (fallback)
        compute_and_move = py_trees.composites.Sequence(
            name="ComputeAndMoveToStrategicPosition", memory=True, children=[
                Compute_strategic_spot(
                    name="ComputeStrategicSpot",
                    get_base_pos=self.get_base_pos,
                    max_radius=self.max_radius,
                    find_free_spot=self.find_free_spot,
                ),
                MoveToStrategicSpot(
                    name="MoveToStrategicSpot",
                    move_factory=self.move_factory,
                ),
            ]
        )

        self.add_children([
            dispute_loose_ball,
            pressurer_actions,
            coverage_actions,
            compute_and_move
        ])
    
    def setup(self, **kwargs):
        return super().setup(**kwargs)


def cond_ball_loose_factory():
    pass

def cond_closest_to_ball_factory():
    pass

def communicate_loose_ball_factory():
    pass

def move_factory_to_ball():
    pass

def take_possession_factory():
    pass

def cond_is_pressurer_factory():
    pass

def cond_not_in_panic_zone_factory():
    pass

def contain_opponent_factory():
    pass

def attempt_tackle_factory():
    pass

def cond_in_panic_zone_factory():
    pass

def clear_ball_factory():
    pass

def cond_is_coverage_factory():
    pass

def cond_pass_in_progress_factory():
    pass

def cond_intercept_time_better_factory():
    pass

def move_to_intercept_factory():
    pass

def cond_opponent_in_zone_factory():
    pass

def cond_pressurer_needs_help_factory():
    pass

def approach_to_contain_factory():
    pass

def cond_dangerous_adversary_free_factory():
    pass

def block_pass_line_factory():
    pass

def cond_last_defender_factory():
    pass

def cond_opponent_advancing_factory():
    pass