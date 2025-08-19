#strategy/actions
import py_trees
from ...robot.bob import Bob
from ...core.blackboard import Blackboard_Manager
from ...core.World_State import World_State
from ...core.event_callbacks import BB_flags_and_values

navigation_flags = BB_flags_and_values.Flags.motion.navigation 
#=======================================================================================#
#                                       IMPLEMENTADOS                                   #
#=======================================================================================#

#---------------------------------------------------------------------------------------#
#                                        BLACKBOARD                                     #
#---------------------------------------------------------------------------------------#
class Set_blackboard_value(py_trees.behaviour.Behaviour):
    """Define um valor no BB """
    def __init__(self, name, key, value):
        super().__init__(name)
        self.key=key 
        self.value=value
        self.bb=Blackboard_Manager.get_instance()
    def update(self): 
        self.bb.set(self.key, self.value)
        return py_trees.common.Status.SUCCESS

class Wait_for_event(py_trees.behaviour.Behaviour):
    """RUNNING até key no bb ser True; SUCCESS quando True"""
    def __init__(self, name, key):
        super().__init__(name); self.key=key; self.bb=Blackboard_Manager.get_instance()
    def update(self):
        return py_trees.common.Status.SUCCESS if bool(self.bb.get(self.key)) else py_trees.common.Status.RUNNING

class Clear_blackboard(py_trees.behaviour.Behaviour):
    """Remove uma chave do BB """
    def __init__(self, name, key):
        super().__init__(name); self.key=key; self.bb=Blackboard_Manager.get_instance()
    def update(self): 
        try: self.bb.clear(self.key)
        finally: return py_trees.common.Status.SUCCESS
