from __future__ import annotations
from typing import Optional

from Behaviour_tree.managers.base_manager import BaseManager
from Behaviour_tree.core.game_state import GameState, RefereeAdapter

from Behaviour_tree.game_states import (
    Behaviour,
    HaltBehaviour,
    StopBehaviour,
    RunningBehaviour,
    ReadyKickoffUsBehaviour,
    ReadyKickoffThemBehaviour,
    ReadyFreekickUsBehaviour,
    ReadyFreekickThemBehaviour,
    ReadyPenaltyUsBehaviour,
    ReadyPenaltyThemBehaviour,
    BallPlacementUsBehaviour,
    BallPlacementThemBehaviour,
)

# mapa central de estados -> classe
_BEHAVIOUR_MAP: dict[GameState, type[Behaviour]] = {
    GameState.HALT: HaltBehaviour,
    GameState.STOP: StopBehaviour,
    GameState.RUNNING: RunningBehaviour,
    GameState.READY_KICKOFF_US: ReadyKickoffUsBehaviour,
    GameState.READY_KICKOFF_THEM: ReadyKickoffThemBehaviour,
    GameState.READY_FREEKICK_US: ReadyFreekickUsBehaviour,
    GameState.READY_FREEKICK_THEM: ReadyFreekickThemBehaviour,
    GameState.READY_PENALTY_US: ReadyPenaltyUsBehaviour,
    GameState.READY_PENALTY_THEM: ReadyPenaltyThemBehaviour,
    GameState.BALL_PLACEMENT_US: BallPlacementUsBehaviour,
    GameState.BALL_PLACEMENT_THEM: BallPlacementThemBehaviour,
}

class TreesManager(BaseManager):
    """
    dono da máquina de estados do jogo.
    - Le referee via World_State
    - traduz para GameState via RefereeAdapter
    - loga transições de estado 
    """
    def __init__(self) -> None:
        super().__init__()
        self._adapter = RefereeAdapter()
        self.current_state: GameState = GameState.UNKNOWN
        self._last_logged_state: Optional[GameState] = None

    def create(self) -> None:
        # inicializa estado como STOP ate receber algo do referee
        self.current_state = GameState.STOP
        self.behaviour: Behaviour | None = self._make_behaviour(self.current_state)
        if self.behaviour:
            self.behaviour.on_enter(prev_state=None)
        self._last_logged_state = None
        self._log_state_change(prev=None, nxt=self.current_state)

    def update(self, dt: float = 0.0) -> None:

        """
        executa um ciclo de atualizacao da maquina de estados de jogo

        este metodo e chamado a cada frame ou ciclo principal do sistema e tem a funcao de:
        1. ler o ultimo pacote do referee recebido via world_state
        2. traduzir o comando atual (ex: halt, stop, prepare_kickoff_yellow, normal_start, etc)
        em um estado interno (gamestate) utilizando o refereeadapter
        3. detectar se houve mudanca de estado em relacao ao frame anterior
        - caso tenha mudado:
            • executa o on_exit do behaviour anterior (limpeza, reset de permissoes)
            • cria e ativa o novo behaviour correspondente ao novo gamestate
            • executa o on_enter do novo behaviour (set de flags e permissoes)
        4. chamar behaviour.update(dt), que:
            • mantem as regras e restricoes do estado atual (halt, stop, running...)
            • atualiza as flags no blackboard (ex: gc_can_move, gc_can_kick, gc_state),
            controlando o que as behaviour trees poderao executar
        5. decidir se as arvores de comportamento devem ser tickadas neste frame
        — normalmente:
            • nenhuma em halt
            • apenas arvores de posicionamento em stop/ready_*
            • todas em running

        em resumo:
        referee -> treesmanager (interpreta e troca behaviour) -> behaviour (define politica) -> blackboard (flags globais) -> behaviour trees (acoes condicionadas)

        parametros:
            dt (float): delta de tempo desde o ultimo frame, se aplicar logica temporal

        """
        #print(self.behaviour)
        # 1) le referee do World_State
        ref = self.ws.get_referee_data()

        # 2) resolve o GameState
        next_state = self._adapter.to_game_state(ref)
        if next_state == GameState.UNKNOWN:
            # fallback seguro 
            print("GAME STATE UNKNOWN (trees_manager.py na update)")
            next_state = GameState.STOP

        # 3) transicao de estado 
        if next_state != self.current_state:
            prev = self.current_state
            # sair do behaviour anterior
            if self.behaviour:
                self.behaviour.on_exit(next_state.name.lower())
            # trocar estado e behaviour
            self.current_state = next_state
            self.behaviour = self._make_behaviour(next_state)
            if self.behaviour:
                self.behaviour.on_enter(prev_state=prev.name.lower())
            self._log_state_change(prev=prev, nxt=next_state)

        # aplicar politica do estado
        if self.behaviour:
            self.behaviour.update(dt)

        #print(self.current_state)

    # -------- Internals -------- #
    def _log_state_change(self, prev: Optional[GameState], nxt: GameState) -> None:
        if nxt != self._last_logged_state:
            if prev is None:
                print(f"[TreesManager] START in state: {nxt.name}")
            else:
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                print(f"[TreesManager] STATE CHANGE: {prev.name} -> {nxt.name}")
            self._last_logged_state = nxt

    def get_state(self) -> GameState:
        return self.current_state
    
    def _make_behaviour(self, st: GameState) -> Behaviour:
        #cria a instancia de Behaviour correspondente ao estado
        cls = _BEHAVIOUR_MAP.get(st, StopBehaviour)
        return cls()
