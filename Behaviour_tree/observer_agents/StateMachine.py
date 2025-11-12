from .Observer import Observer
from .Observer import EventClass
from typing import List
from Behaviour_tree.robot.BobManager import BobManager
from ..core.event_callbacks import EventEnum
from ..core.event_callbacks import TreePaths
from SSL_configuration.configuration import Configuration
from ..core.blackboard import Blackboard_Manager
from ..trees.goalkeeper.goalkeeper_tree import get_goalkeeper_tree
from ..trees.defender.defender_tree import get_defender_tree
from ..trees.halt.Halt import get_halt_tree
from ..trees.ofensive_sup.offensive_suport_tree import get_off_sup_tree
from ..trees.pivo.pivo import get_pivo_tree
from ..trees.stop.stop_tree import get_stop_tree


_bb = Blackboard_Manager.get_instance()

class StateMachine(Observer):

    def __init__(self):
        super().__init__()
        self.events = {
            EventEnum.FOES_HAS_BALL:  EventClass(EventEnum.FOES_HAS_BALL, None), 
            EventEnum.PASSA_MEIO:     EventClass(EventEnum.PASSA_MEIO, None), 
            EventEnum.TEAM_HAS_BALL:  EventClass(EventEnum.TEAM_HAS_BALL, None),
            EventEnum.FOES_FREE_KICK:  EventClass(EventEnum.FOES_FREE_KICK, None),
            EventEnum.TEAM_FREE_KICK:  EventClass(EventEnum.TEAM_FREE_KICK, None),
            EventEnum.FOES_PENALTY:  EventClass(EventEnum.FOES_PENALTY, None),
            EventEnum.TEAM_PENALTY:  EventClass(EventEnum.TEAM_PENALTY, None),
            EventEnum.HALT:  EventClass(EventEnum.HALT, None),
            EventEnum.STOP:  EventClass(EventEnum.STOP, None),
        }

        self.config = Configuration.getObject()

        self.bobManager: BobManager = BobManager.get_instance()

        self.stateDef = {
            "AtkPosse":     ("D", "C", "B"),
            "DefPerca":     ("D", "E", "C"),
            "DefRec":       ("D", "E", "G"),
            "TeamFreeKick": ("A", "B", "C"),
            "FoesFreeKick": ("D", "E", "G"),
            "Halt":         ("I1", "I2", "I3"),
            "TeamPenalty":  ("C", "H2", "H3"),
            "FoesPenalty":  ("D", "H2", "H3"),
            "Stop":         ("H1", "H2", "H3"),
        }
        #Relação dos números com as árvores para dar tick
        self.treesRelation = {
            "A": TreePaths.KICKER,
            "B": TreePaths.SUPORT_OF,
            "C": TreePaths.PIVO,
            "D": TreePaths.GOALKEEPER,
            "E": TreePaths.DEF_RECUADO,
            "G": TreePaths.BARRIER,
            "H1": TreePaths.STOP1,
            "H2": TreePaths.STOP2,
            "H3": TreePaths.STOP3,
            "I1": TreePaths.HALT1,
            "I2": TreePaths.HALT2,
            "I3": TreePaths.HALT3,
            "J1": TreePaths.EXPULSO1,
            "J2": TreePaths.EXPULSO2,
            "J3": TreePaths.EXPULSO3,
        }

        self.treesInstances = {
            TreePaths.KICKER: None,
            TreePaths.BARRIER: None,
            TreePaths.PIVO: get_pivo_tree(TreePaths.PIVO),
            TreePaths.SUPORT_OF: get_off_sup_tree(TreePaths.SUPORT_OF),
            TreePaths.GOALKEEPER: get_goalkeeper_tree(TreePaths.GOALKEEPER),
            TreePaths.DEF_RECUADO: get_defender_tree(TreePaths.DEF_RECUADO),
            TreePaths.STOP1: get_stop_tree(TreePaths.STOP1),
            TreePaths.STOP2: get_stop_tree(TreePaths.STOP2),
            TreePaths.STOP3: get_stop_tree(TreePaths.STOP3),
            TreePaths.HALT1: get_halt_tree(TreePaths.HALT1),
            TreePaths.HALT2: get_halt_tree(TreePaths.HALT2),
            TreePaths.HALT3: get_halt_tree(TreePaths.HALT3),
        }

        self.normalState = "DefRec"
        self.specialState = None

    def tickTrees(self):
        state = self.normalState
        if self.specialState is not None:
            state = self.specialState
        for treeCode in self.stateDef.get(state):
            tree = self.treesRelation.get(treeCode)
            if not tree:
                continue
            treeInst = self.treesInstances.get(tree)
            if not treeInst:
                continue
            treeInst.tick()
        

    def setTrees(self):
        _bb.set(TreePaths.KICKER, None)
        _bb.set(TreePaths.BARRIER, None)
        _bb.set(TreePaths.DEF_ADD, None)
        _bb.set(TreePaths.DEF_RECUADO, None)
        _bb.set(TreePaths.EXPULSO1, None)
        _bb.set(TreePaths.EXPULSO2, None)
        _bb.set(TreePaths.EXPULSO3, None)
        _bb.set(TreePaths.GOALKEEPER, None)
        _bb.set(TreePaths.HALT1, None)
        _bb.set(TreePaths.HALT2, None)
        _bb.set(TreePaths.HALT3, None)
        _bb.set(TreePaths.PIVO, None)
        _bb.set(TreePaths.SUPORT_OF, None)
        _bb.set(TreePaths.STOP1, None)
        _bb.set(TreePaths.STOP2, None)
        _bb.set(TreePaths.STOP3, None)

        self.updateBobTrees()
    
    def notify(self, event: EventClass):
        ev = self.events.get(event.name)
        
        if ev is None:
            return  # ignora eventos que a SM não conhece
        ev.value = event.value
        self.update()

    def updateBobTrees(self):
        state = self.specialState
        if state is None:
            state = self.normalState
        tree_codes = self.stateDef.get(state, ())
        bob_values = list(self.bobManager.bobs.values())
        for code, value in zip(tree_codes, bob_values):
            path = self.treesRelation.get(code)
            if path is not None:
                _bb.set(path, value)
                #print(path, value.robot_id)


    def updateState(self):

        if self.events[EventEnum.FOES_PENALTY].value == True and self.specialState is None:
            self.specialState = "FoesPenalty"
            return True

        if self.events[EventEnum.TEAM_PENALTY].value == True and self.specialState is None:
            self.specialState = "TeamPenalty"
            return True
        
        if self.events[EventEnum.TEAM_FREE_KICK].value == True and self.specialState is None:
            self.specialState = "TeamFreeKick"
            return True
        
        if self.events[EventEnum.FOES_FREE_KICK].value == True and self.specialState is None:
            self.specialState = "FoesFreeKick"
            return True
        
        if self.events[EventEnum.HALT].value == True and self.specialState is None:
            self.specialState = "Halt"
            return True
        
        if self.events[EventEnum.STOP].value == True and self.specialState is None:
            self.specialState = "Stop"
            return True
        match(self.specialState):
            case "Stop":
                if self.events[EventEnum.STOP].value == False:
                    self.specialState = None
                    return True

            case "Halt":
                if self.events[EventEnum.HALT].value == False:
                    self.specialState = None
                    return True

            case "FoesFreeKick":
                if self.events[EventEnum.FOES_FREE_KICK].value == False:
                    self.specialState = None
                    return True
            
            case "TeamFreeKick":
                if self.events[EventEnum.TEAM_FREE_KICK].value == False:
                    self.specialState = None
                    return True

            case "TeamPenalty":
                if self.events[EventEnum.TEAM_PENALTY].value == False:
                    self.specialState = None
                    return True

            case "FoesPenalty":
                if self.events[EventEnum.FOES_PENALTY].value == False:
                    self.specialState = None
                    return True
        if self.specialState is not None:
            return

        match(self.normalState):
            case "AtkPosse":
                if self.events[EventEnum.TEAM_HAS_BALL].value == False and self.events[EventEnum.FOES_HAS_BALL].value == True:
                    self.normalState = "DefPerca"
                    return True
            
            case "DefPerca":
                if self.events[EventEnum.PASSA_MEIO].value == True:
                    self.normalState = "DefRec"
                    return True
            
            case "DefRec":
                if self.events[EventEnum.TEAM_HAS_BALL].value == True and self.events[EventEnum.FOES_HAS_BALL].value == False:
                    self.normalState = "AtkPosse"
                    return True
                
        return False

    def update(self):
        initialNormalState = self.normalState
        inititalSpecialState = self.specialState
        while self.updateState() == True:
            continue
        if self.specialState is not None:
            if inititalSpecialState != self.specialState:
                self.updateBobTrees()

            return
        
        if initialNormalState != self.normalState or inititalSpecialState != self.specialState:
            self.updateBobTrees()
        
        
    
        