from .Observer import Observer
from .Observer import EventClass
from typing import List
from Behaviour_tree.robot.BobManager import BobManager
from ..core.event_callbacks import EventEnum
from ..core.event_callbacks import TreePaths
from SSL_configuration.configuration import Configuration
from ..core.blackboard import Blackboard_Manager


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

        self.normalState = "DefRec"
        self.specialState = None

        # if self.config.startWithBall:
        #     self.stack.append("TeamFreeKick")
        # else:
        #     self.stack.append("FoesFreeKick")

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


    # def updateBobs(self):
    #     for bob in self.bobs:
    #         bob.update()
    
    def tickTrees(self):
        ...

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
                print(path, value.robot_id)


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
        
        
        
    #2 problemas ainda, o loop infinito, so fazer com variaveis separadas para estados especiais, e o fato do estado inicial nao ser um estado in game de vdd
        