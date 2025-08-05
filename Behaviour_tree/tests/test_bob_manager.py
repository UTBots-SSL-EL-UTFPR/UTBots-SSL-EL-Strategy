# tests/test_bob_manager.py

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bob_manager import BobManager
from core.Field import RobotID
from robot.bob import Bob
from trees.tree import Tree


def test_bob_manager_initialization():
    """
    Testa se o BobManager instancia corretamente os Bobs e suas árvores.
    """
    manager = BobManager()

    for robot_id in [RobotID.Kamiji, RobotID.Defender, RobotID.Goalkeeper]:
        assert robot_id in manager.bobs
        assert isinstance(manager.get_bob(robot_id), Bob)
        assert robot_id in manager.trees
        assert isinstance(manager.get_tree(robot_id), Tree)


def test_bob_manager_update_and_tick():
    """
    Testa se os métodos update_all e tick_all executam sem erro.
    """
    manager = BobManager()
    manager.update_all()
    manager.tick_all()
    assert True
