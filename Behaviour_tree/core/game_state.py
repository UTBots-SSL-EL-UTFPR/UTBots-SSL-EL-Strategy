from __future__ import annotations
from enum import Enum, auto
from typing import Any, Optional

try:
    from SSL_configuration.configuration import Configuration
except Exception:
    Configuration = None  # fallback seguro


#os estados aqui vem tudo do livro de regras
class GameState(Enum):
    HALT = auto()
    STOP = auto()
    READY_KICKOFF_US = auto()       #no livro é PREPARE_KICKOFF_YELLOW / _BLUE
    READY_KICKOFF_THEM = auto()
    READY_FREEKICK_US = auto()
    READY_FREEKICK_THEM = auto()
    READY_PENALTY_US = auto()
    READY_PENALTY_THEM = auto()
    BALL_PLACEMENT_US = auto()
    BALL_PLACEMENT_THEM = auto()
    RUNNING = auto()
    UNKNOWN = auto()


class RefereeAdapter:
    """
    traduz referee_data -> GameState, usando a cor do nosso time
    """
    def __init__(self) -> None:
        self._team_color = self._read_team_color()  # "yellow" | "blue" | None

    def _read_team_color(self) -> Optional[str]:
        if Configuration is None:
            print("cor invalida de time!!!!!!!!!!!")
            return None
        try:
            cfg = Configuration.getObject()
            color = getattr(cfg, "team_collor", None)  # no arquivo ta collor com 2 L msm ent fodasse kkkk
            if isinstance(color, str):
                c = color.strip().lower()
                if c in ("yellow", "blue"):
                    return c
        except Exception:
            pass
        return None  # se nao soubermos, so um none

    def _is_us_color(self, name_upper: str) -> Optional[bool]:
        """
        retorna true se o comando do referee menciona a nossa cor, False se menciona a do oponente,
        ou None se não der para inferir.
        """
        if self._team_color is None:
            return None
        if "YELLOW" in name_upper:
            return self._team_color == "yellow"
        if "BLUE" in name_upper:
            return self._team_color == "blue"
        return None

    def to_game_state(self, referee_msg: Optional[Any])-> GameState:
        """
        aceita o objeto bruto vindo do World_State.get_referee_data()
        tenta ler referee_msg.command (enum/string); devolve GameState
        em caso de dúvida, retorna STOP 
        """
        if referee_msg is None:
            return GameState.UNKNOWN

        # extrai nome do comando 
        #dar atencao aqui pq nao tenho ctz de como vem esse comando ainda
        cmd_name = None
        try:
            cmd = getattr(referee_msg, "command", None)
            if hasattr(cmd, "name"):
                cmd_name = cmd.name
            elif isinstance(cmd, str):
                cmd_name = cmd
            else:
                cmd_name = getattr(referee_msg, "name", None)
        except Exception:
            cmd_name = None

        if not cmd_name:
            print("NAO ACHOU CMD_NAME")
            return GameState.STOP  # seguro

        name = str(cmd_name).upper()

        # comandos globais (pros 2 times é igaul)
        if "HALT" in name:
            return GameState.HALT
        if "STOP" in name:
            return GameState.STOP
        if "NORMAL_START" in name or "FORCE_START" in name:
            return GameState.RUNNING

        # decidir US/THEM por cor
        us = self._is_us_color(name)

        # kickoff
        if "PREPARE_KICKOFF" in name:
            if us is True:
                return GameState.READY_KICKOFF_US
            if us is False:
                return GameState.READY_KICKOFF_THEM
            print("NAO DEU PRA INFERIR QUAL TIME SOMOS (game_state.py kickoff)")
            return GameState.STOP  # se não der pra inferir, joga seguro

        # free kick (direct/indirect)
        if (
            "PREPARE_DIRECT_FREE" in name
            or "PREPARE_INDIRECT_FREE" in name
            or "PREPARE_FREE_KICK" in name
        ):
            if us is True:
                return GameState.READY_FREEKICK_US
            if us is False:
                return GameState.READY_FREEKICK_THEM
            print("NAO DEU PRA INFERIR QUAL TIME SOMOS (game_state.py freekick)")
            return GameState.STOP

        # penalty
        if "PREPARE_PENALTY" in name or ("PENALTY" in name and "PREPARE" in name):
            if us is True:
                return GameState.READY_PENALTY_US
            if us is False:
                return GameState.READY_PENALTY_THEM
            print("NAO DEU PRA INFERIR QUAL TIME SOMOS (game_state.py penalty)")
            return GameState.STOP

        # ball placement
        if "BALL_PLACEMENT" in name or "PLACEMENT" in name:
            if us is True:
                return GameState.BALL_PLACEMENT_US
            if us is False:
                return GameState.BALL_PLACEMENT_THEM
            print("NAO DEU PRA INFERIR QUAL TIME SOMOS (game_state.py ballPlacement)")
            return GameState.STOP

        # default seguro, se nao sabe onde ta, fica em stop
        return GameState.STOP