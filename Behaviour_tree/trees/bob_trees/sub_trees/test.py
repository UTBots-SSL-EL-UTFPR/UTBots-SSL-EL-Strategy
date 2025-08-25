#teste movimentação
from Behaviour_tree.core.World_State import World_State, RobotID
from Behaviour_tree.robot.bob import Bob
import time
import py_trees as pt
from utils.pose2D import Pose2D
import time
from Behaviour_tree.core.event_callbacks import BB_flags_and_values
from Behaviour_tree.core.blackboard import Blackboard_Manager
from ....behaviors.common import condition as condition_nodes
from ....behaviors.common import actions as action_nodes
from ...tree import Tree

from Behaviour_tree.bob_manager import BobManager
navigation_flags = BB_flags_and_values.Flags.motion.navigation 
positions = BB_flags_and_values.Values.Positions

TICK_INTERVAL = 0.1 
UPDATE_INTERVAL = TICK_INTERVAL / 2 


class PrintNode(pt.behaviour.Behaviour):

    def __init__(self, name: str = "PrintNode"):
        super().__init__(name=name)
        self.robot : Bob | None = None
        self._bb = Blackboard_Manager.get_instance()

    def setup(self, **kwargs) -> None:
        self.robot = kwargs.get("bob")
        if self.robot:
            print("setup")

    def initialise(self) -> None:
        print("initialize")

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE
        
        if self._bb.get(
            f"{self.robot.robot_id.name}{navigation_flags.target_reached}"
            ):
            return pt.common.Status.SUCCESS
        if self.robot.state.target_position:
            print(self.robot.state.target_position)
            self.robot.move_oriented()
        return pt.common.Status.RUNNING
    
    def terminate(self, new_status: pt.common.Status) -> None:
        if self.robot is None or self.robot.state is None:
            return 
        if self.robot.state:
            self.robot.state.target_position = None

    def shutdown(self) -> None:
        print("shutdown")


def main() -> None:
    bob_state = BobManager.get_object()
    wd = World_State.get_object()
    kamiji = bob_state.get_bob(RobotID.Kamiji)

    if kamiji is None: 
        return

    teste = PrintNode()
    sequence = pt.composites.Sequence("sequencia",True, [teste])
    root = pt.trees.BehaviourTree(sequence)

    print("\n--- SETUP ---")
    setup_args = {
        "bob": kamiji,           
        "planner": 11
    }
    root.setup(timeout=1.0, visitor=None, **setup_args)


    delay = 2
    t0 = time.time()

    while time.time() <= delay + t0:
        wd.update()

    t0 = time.time()
    delay = 0.01

    print("\n--- LOOP ---")
    wd.update()
    bob_state.update_all()
    bob_state.set_kicker_position(RobotID.Kamiji)

    for pos in kamiji.state.path:
        print(f" fazendo {pos}")

    while True:
        if time.time() >= delay + t0:
            wd.update()
            bob_state.update_all()
            root.tick()
            t0 = time.time()


    

if __name__ == "__main__":
    main()
