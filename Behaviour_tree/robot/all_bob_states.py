"""Singleton AllBobStates

Fornece acesso às informações (ex.: posições) de todos os Bob_State registrados
excluindo o chamador. Cada método chama os getters dos outros estados em tempo real.

Uso esperado dentro de um Bob_State: 
    outras_pos = self.get_all_bobs.Get_bobs_positions(self)
"""
from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # somente para type checking, evita import circular em runtime
    from .bob_state import Bob_State


class AllBobStates:
    _instance: "AllBobStates" | None = None

    def __init__(self) -> None:
        if AllBobStates._instance is not None:
            raise RuntimeError("Use AllBobStates.get_instance()")
        self._states: Dict[object, "Bob_State"] = {}

    @classmethod
    def get_instance(cls) -> "AllBobStates":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ---------------- Registro ----------------
    def register(self, state: "Bob_State") -> None:
        """Registra (ou atualiza) um Bob_State pelo seu robot_id."""
        self._states[state.robot_id] = state

    def unregister(self, robot_id) -> None:
        self._states.pop(robot_id, None)

    # ---------------- Internos ----------------
    def _others(self, caller: "Bob_State") -> Iterable["Bob_State"]:
        cid = caller.robot_id
        for rid, st in self._states.items():
            if rid != cid:
                yield st

    # ---------------- Consultas (excluem o chamador) ----------------
    def Get_bobs_positions(self, caller: "Bob_State") -> List[tuple[float, float]]:
        """Retorna lista das posições (x,y) dos outros bobs."""
        return [s.get_position() for s in self._others(caller)]

    def get_bobs_velocities(self, caller: "Bob_State") -> List[tuple[float, float]]:
        return [s.get_velocity() for s in self._others(caller)]

    def get_bobs_roles(self, caller: "Bob_State") -> List[object]:
        return [s.get_role() for s in self._others(caller)]

__all__ = ["AllBobStates"]
