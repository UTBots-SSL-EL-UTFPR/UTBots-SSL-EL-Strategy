from .Observer import Observer
from .Observer import Event
from typing import List
from ..robot.bob import Bob
from ..core.event_callbacks import EventEnum

class StateMachine(Observer):

    def __init__(self, bobs: List[Bob]):
        self.events: List[Event] = {
            EventEnum.FOES_HAS_BALL:  Event(EventEnum.FOES_HAS_BALL, None), 
            EventEnum.PASSA_MEIO:     Event(EventEnum.PASSA_MEIO, None), 
            EventEnum.TEAM_HAS_BALL:  Event(EventEnum.TEAM_HAS_BALL, None)
        }

        self.bobs: List[Bob] = bobs
        self.stateDef = {
            "GameStart":    ("H", "H", "H"),
            "AtkPosse":     ("D", "C", "B"),
            "DefPerca":     ("D", "E", "F"),
            "DefRec":       ("D", "E", "G"),
            "TeamFreeKick": ("A", "B", "C"),
            "FoesFreeKick": ("D", "E", "G"),
            "Halt":         ("I", "I", "I"),
            "TeamPenalty":  ("C", "H", "H"),
            "FoesPenalty":  ("D", "H", "H"),
            "Stop":         ("H", "H", "H"),
        }
        #Relação dos números com as árvores para dar tick
        self.treesRelation = {}

        self.stack = ["GameStart"]

    
    def notify(self, event: Event):
        ev = next((e for e in self.events if e.name == event.name), None)
        if ev is None: raise Exception("???? you could not be here")

        ev.value = event.value
        self.update()

    def updateBobs(self):
        for bob in self.bobs:
            bob.update()
    
    def tickTrees(self):
        ...

    def update(self):
        top = self.stack[-1]

        match(top):
            case "AtkPosse":
                if self.events[EventEnum.TEAM_HAS_BALL] == False and self.events[EventEnum.FOES_HAS_BALL] == True:
                    self.stack.pop()
                    self.stack.append("DefPerca")
            
            case "DefPerca":
                if self.events[EventEnum.PASSA_MEIO] == True:
                    self.stack.pop()
                    self.stack.append("DefRec")
            
            case "DefRec":
                if self.events[EventEnum.TEAM_HAS_BALL] == True and self.events[EventEnum.FOES_HAS_BALL] == False:
                    self.stack.pop()
                    self.stack.append("AtkPosse")
        