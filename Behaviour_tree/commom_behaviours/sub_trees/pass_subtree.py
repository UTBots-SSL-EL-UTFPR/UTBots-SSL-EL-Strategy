# pass subtree.py
import py_trees

import Behaviour_tree.helpers as hp
from Behaviour_tree.robot.bob import Bob

from ..condition import HasBall


def get_pass_subtree(path: str) -> py_trees.composites.Sequence:
    # TODO
    has_ball = HasBall(path)

    pass_subtree = py_trees.composites.Sequence(
        "arvore de chute", True, children=[has_ball]
    )
    return pass_subtree
