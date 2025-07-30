import pytest
from core.blackboard import Blackboard_Manager
from core.event_manager import Event_Manager
from core.event_callbacks import EventType, subscribe_all
from core.Field import RobotID

@pytest.fixture(autouse=True)
def clean_state():
    Blackboard_Manager.get_instance().clear()
    Event_Manager.clear()
    subscribe_all()

def simulate_update_robot_stuck(robot_id):# Simula BobState.update()
    Event_Manager.publish(EventType.ROBOT_STUCK.value, robot_id=robot_id)

def test_robot_stuck_event_affects_only_target_robot():
    bb = Blackboard_Manager.get_instance()
    #apenas Kamiji travado
    simulate_update_robot_stuck(RobotID.Kamiji)
    assert bb.get(f"{RobotID.Kamiji.value}_is_stuck") is True

    # Valida que outros bobs NÃO estão marcados como travados
    for other_robot in RobotID:
        if other_robot != RobotID.Kamiji:
            assert bb.get(f"{other_robot.value}_is_stuck") is None

def test_multiple_event_publish_is_idempotent():
    bb = Blackboard_Manager.get_instance()

    # Dispara o mesmo evento várias vezes para o mesmo robô
    for _ in range(5):
        simulate_update_robot_stuck(RobotID.Kamiji)

    # Verifica flag
    assert bb.get(f"{RobotID.Kamiji.value}_is_stuck") is True

def test_no_false_positives_on_empty_state():
    bb = Blackboard_Manager.get_instance()
    for robot in RobotID:
        assert bb.get(f"{robot.value}_is_stuck") is None
