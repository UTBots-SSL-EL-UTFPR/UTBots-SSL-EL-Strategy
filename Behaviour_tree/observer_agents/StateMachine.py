from .Observer import Observer
from .Observer import Event
from typing import List
from ..bob_manager import BobManager
from ..core.event_callbacks import EventEnum
from ..core.event_callbacks import TreePaths
from SSL_configuration.configuration import Configuration
from ..core.blackboard import Blackboard_Manager


_bb = Blackboard_Manager.get_instance()

class StateMachine(Observer):

    def __init__(self, bobManager: BobManager):
        self.events = {
            EventEnum.FOES_HAS_BALL:  Event(EventEnum.FOES_HAS_BALL, None), 
            EventEnum.PASSA_MEIO:     Event(EventEnum.PASSA_MEIO, None), 
            EventEnum.TEAM_HAS_BALL:  Event(EventEnum.TEAM_HAS_BALL, None),
            EventEnum.FOES_FREE_KICK:  Event(EventEnum.FOES_FREE_KICK, None),
            EventEnum.TEAM_FREE_KICK:  Event(EventEnum.TEAM_FREE_KICK, None),
            EventEnum.FOES_PENALTY:  Event(EventEnum.FOES_PENALTY, None),
            EventEnum.TEAM_PENALTY:  Event(EventEnum.TEAM_PENALTY, None),
            EventEnum.HALT:  Event(EventEnum.HALT, None),
            EventEnum.STOP:  Event(EventEnum.STOP, None),
        }

        self.config = Configuration.getObject()

        self.bobManager: BobManager = bobManager

        self.stateDef = {
            "AtkPosse":     ("D", "C", "B"),
            "DefPerca":     ("D", "E", "F"),
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
            "F": TreePaths.DEF_ADD,
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

        self.stack = []

        if self.config.startWithBall:
            self.stack.append("TeamFreeKick")
        else:
            self.stack.append("FoesFreeKick")

    def setTrees(self):
        _bb.set(TreePaths.KICKER, None)
        _bb.set(TreePaths.BARRIER, None)
        _bb.set(TreePaths.DEF_ADD, None)
        _bb.set(TreePaths.DEF_RECUADO, None)
        _bb.set(TreePaths.EXPULSO1, None)
        _bb.set(TreePaths.EXPULSO2, None)
        _bb.set(TreePaths.EXPULSO2, None)
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

        

    
    def notify(self, event: Event):
        ev: Event = self.events[event.name]
        if ev is not None:
            ev.value = event.value
            self.update()

    # def updateBobs(self):
    #     for bob in self.bobs:
    #         bob.update()
    
    def tickTrees(self):
        ...

    def updateBobTrees(self):
        for i in range(0,2):
            itemsList = list(self.bobManager.bobs.items())

            tree = self.stateDef[self.stack[-1]]
            _, value = itemsList[i]
            _bb.set(self.treesRelation[tree], value)

    def updateState(self):
        top = self.stack[-1]

        if self.events[EventEnum.FOES_PENALTY]:
            self.stack.append("FoesPenalty")
            return True

        if self.events[EventEnum.TEAM_PENALTY]:
            self.stack.append("TeamPenalty")
            return True
        
        if self.events[EventEnum.TEAM_FREE_KICK]:
            self.stack.append("TeamFreeKick")
            return True
        
        if self.events[EventEnum.FOES_FREE_KICK]:
            self.stack.append("FoesFreeKick")
            return True
        
        if self.events[EventEnum.HALT]:
            self.stack.append("Halt")
            return True
        
        if self.events[EventEnum.STOP]:
            self.stack.append("Stop")
            return True

        match(top):
            case "Stop":
                if self.events[EventEnum.STOP] == False:
                    self.stack.pop()
                    return True

            case "Halt":
                if self.events[EventEnum.HALT] == False:
                    self.stack.pop()
                    return True

            case "FoesFreeKick":
                if self.events[EventEnum.FOES_FREE_KICK] == False:
                    self.stack.pop()
                    return True
            
            case "TeamFreeKick":
                if self.events[EventEnum.TEAM_FREE_KICK] == False:
                    self.stack.pop()
                    return True

            case "TeamPenalty":
                if self.events[EventEnum.TEAM_PENALTY] == False:
                    self.stack.pop()
                    return True

            case "FoesPenalty":
                if self.events[EventEnum.FOES_PENALTY] == False:
                    self.stack.pop()
                    return True

            case "AtkPosse":
                if self.events[EventEnum.TEAM_HAS_BALL] == False and self.events[EventEnum.FOES_HAS_BALL] == True:
                    self.stack.pop()
                    self.stack.append("DefPerca")
                    return True
            
            case "DefPerca":
                if self.events[EventEnum.PASSA_MEIO] == True:
                    self.stack.pop()
                    self.stack.append("DefRec")
                    return True
            
            case "DefRec":
                if self.events[EventEnum.TEAM_HAS_BALL] == True and self.events[EventEnum.FOES_HAS_BALL] == False:
                    self.stack.pop()
                    self.stack.append("AtkPosse")
                    return True

    def update(self):
        if self.updateState():
            self.updateBobTrees()
        
        