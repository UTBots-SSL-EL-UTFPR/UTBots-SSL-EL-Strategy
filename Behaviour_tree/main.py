import logging
import time

from Behaviour_tree.core.World_State import World_State
from Behaviour_tree.robot.BobManager import BobManager

from .observer_agents.EventNotifier import EventNotifier
from .observer_agents.StateMachine import StateMachine

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class Game:
    def __init__(self) -> None:
        self.bobManager: BobManager = BobManager.get_instance()
        self.stateMachine = StateMachine()
        self.eventNotifier = EventNotifier.get_instance()
        self.wd = World_State.get_object()

    def update(self):
        self.bobManager.update()
        self.wd.update()
        self.stateMachine.tickTrees()


def main():
    game = Game()

    update_delay = 0.005
    # print_delay = 0.5
    # tPrint = time.time()
    tUpdate = time.time()

    while True:
        if time.time() >= update_delay + tUpdate:
            game.update()
            print(game.stateMachine.normalState)
            tUpdate = time.time()


if __name__ == "__main__":
    main()
