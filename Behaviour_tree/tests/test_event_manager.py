import pytest

from Behaviour_tree.core.Field import RobotID
from core.event_manager import Event_Manager
from core.event_manager import EventType

@pytest.fixture(autouse=True)
def reset_event_manager():
    """Garante que o Event_Manager esteja limpo antes de cada teste."""
    Event_Manager.clear()

def test_event_subscription_and_publish():
    resultado = {}

    def on_event(robot_id):
        resultado["robot"] = robot_id

    Event_Manager.subscribe(EventType.ROBOT_STUCK.value, on_event)
    Event_Manager.publish(EventType.ROBOT_STUCK.value, robot_id=RobotID.Kamiji)

    assert resultado["robot"] == RobotID.Kamiji

def test_multiple_callbacks_for_same_event():
    chamadas = []

    def callback1(robot_id): chamadas.append("cb1")
    def callback2(robot_id): chamadas.append("cb2")

    Event_Manager.subscribe(EventType.GOAL_OPEN.value, callback1)
    Event_Manager.subscribe(EventType.GOAL_OPEN.value, callback2)

    Event_Manager.publish(EventType.GOAL_OPEN.value, robot_id=RobotID.GOALKEEPER)

    assert chamadas == ["cb1", "cb2"]

def test_clear_specific_event():
    chamadas = []

    def callback(robot_id): chamadas.append("called")

    Event_Manager.subscribe(EventType.TARGET_REACHED.value, callback)
    Event_Manager.clear(EventType.TARGET_REACHED.value)

    Event_Manager.publish(EventType.TARGET_REACHED.value, robot_id=RobotID.DEFENDER)
    assert chamadas == []

def test_clear_all_events():
    chamadas = []

    def callback(robot_id): chamadas.append("called")

    Event_Manager.subscribe(EventType.ROBOT_STUCK.value, callback)
    Event_Manager.subscribe(EventType.GOAL_OPEN.value, callback)

    Event_Manager.clear()
    Event_Manager.publish(EventType.ROBOT_STUCK.value, robot_id=RobotID.Kamiji)
    Event_Manager.publish(EventType.GOAL_OPEN.value, robot_id=RobotID.DEFENDER)

    assert chamadas == []
