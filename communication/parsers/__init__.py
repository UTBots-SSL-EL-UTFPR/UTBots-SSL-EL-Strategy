# Importa e expõe a classe principal de parsing do referee
from .referee_parser import RefereeParser
#from .vision_parser import VisionParser

# Caso você tenha outros parsers no futuro, já pode preparar assim:
# from .team_comm_parser import TeamCommParser

__all__ = [
    "RefereeParser",
    "VisionParser",
    # "TeamCommParser",
]
