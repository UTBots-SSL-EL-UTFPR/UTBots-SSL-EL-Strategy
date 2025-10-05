from enum import Enum
from typing import Dict, Optional

from Behaviour_tree.core.World_State import FoesID

from .foes import FoesState


class FoesManager:
    """
    Agrega e gerencia o estado de todos os robôs adversários.
    """

    def __init__(self):
        """
        Inicializa o gerenciador, criando uma instância de Foes_State para cada
        ID de adversário definido no Enum FoesID.
        """
        self.foes: Dict[FoesID, FoesState] = {}

        for foe_id in FoesID:
            self.foes[foe_id] = FoesState(id=foe_id)

    def update(self):
        """
        Chama o método update() de cada instância de Foes_State gerenciada.
        """
        for foe_state in self.foes.values():
            foe_state.update()

    def get_foe(self, foe_id: FoesID) -> Optional[FoesState]:
        """
        Retorna a instância de um adversário específico.
        """
        return self.foes.get(foe_id)
