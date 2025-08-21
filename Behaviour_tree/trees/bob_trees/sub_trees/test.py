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
            print(self.robot.robot_id)
        print("setup")

    def initialise(self) -> None:
        print("initialize")

    def update(self) -> pt.common.Status:
        if self.robot is None or self.robot.state is None:
            return pt.common.Status.FAILURE
        self.robot.state.target_position
        if self._bb.get(
            f"{self.robot.robot_id.name}{navigation_flags.target_reached}"
            ):
            return pt.common.Status.SUCCESS
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
    bob = Bob(RobotID.Kamiji)
    if bob.state is None:
        return
    bob.state.reset()
    bob.set_movment(Pose2D(0,0,0))
    wd = World_State.get_object()

    teste = PrintNode()
    sequence = pt.composites.Sequence("sequencia",True, [teste])
    root = pt.trees.BehaviourTree(sequence)

    print("\n--- SETUP ---")
    setup_args = {
        "bob": bob,           
        "planner": 11
    }
    root.setup(timeout=1.0, visitor=None, **setup_args)

    print("\n--- LOOP ---")
    t0 = time.time()
    delta = 0.1
    wd.update()
    while True:
        if(time.time() >= t0 + delta):
            wd.update()
            print(55)
            t0 = time.time()
        bob.update()
        root.tick()
        




if __name__ == "__main__":
    main()
