import pytest
from core.blackboard import Blackboard_Manager

@pytest.fixture(autouse=True)
def clean_blackboard():
    """Limpa o blackboard antes de cada teste"""
    Blackboard_Manager.get_instance().clear()

def test_set_and_get():
    bb = Blackboard_Manager.get_instance()
    bb.set("test_key", 42)
    assert bb.get("test_key") == 42

def test_get_with_default():
    bb = Blackboard_Manager.get_instance()
    assert bb.get("nonexistent_key") == None

def test_clear_specific_key():
    bb = Blackboard_Manager.get_instance()
    bb.set("key1", "val1")
    bb.set("key2", "val2")
    bb.clear("key1")
    assert bb.get("key1") is None
    assert bb.get("key2") == "val2"

def test_clear_all_keys():
    bb = Blackboard_Manager.get_instance()
    bb.set("a", 1)
    bb.set("b", 2)
    bb.clear()
    assert bb.get("a") is None
    assert bb.get("b") is None
