from Behaviour_tree.behaviors.common import actions, condition
from typing import Callable, Tuple, Optional
from utils.pose2D import Pose2D
import py_trees
from Behaviour_tree.robot.bob import Bob
import py_trees
from typing import Callable, Tuple, Optional
from Behaviour_tree.core.blackboard import Blackboard_Manager


class SupportOffensive(py_trees.composites.Selector):
    """
    Subárvore suporte_ofensivo com prioridade:
      1. Finalizar se tem a bola
      2. Capturar sobra
      3. Posicionar como opção de passe (calc pos e mover)
    """

    def __init__(
        self,
        name: str,
        bob : Bob,
        max_radius: int = 700,
    ):
        super().__init__(name=name, memory=True)
        self._bb = Blackboard_Manager.get_instance()
        self.bob = bob
        self.max_radius = max_radius

        # 1. CHUTE PRO GOL 
        # #TODO

        # 2. Capturar sobra (bola visível e alcançável)

        bx, by = get_ball_pos()
        capture_loose = py_trees.composites.Sequence(
            name="CaptureLooseBall", memory=True, children=[
                cond_ball_visible_factory(),
                cond_ball_reachable_factory(),
                move_factory(bx, by),
                take_possession_factory(),
            ]
        )

        # 3. Posicionar-se como opção de passe
        compute_and_move = py_trees.composites.Sequence(
            name="ComputeAndMoveToSupport", memory=True, children=[
                Compute_suport_spot(
                    name="ComputeSupportSpot",
                    get_base_pos=self.get_base_pos,
                    max_radius=self.max_radius,
                    find_free_spot=self.find_free_spot,
                ),
                MoveToSupportSpot(
                    name="MoveToSupportSpot",
                    move_factory=self.move_factory,
                ),
            ]
        )

        return_to_base = py_trees.composites.Sequence(
            name="ReturnToBase", memory=False, children=[
                # fallback simples: volta à base
                move_factory(*self.get_base_pos()),
            ]
        )

        position_for_pass = py_trees.composites.Selector(
            name="PositionForPass", memory=False, children=[
                compute_and_move,
                return_to_base,
            ]
        )

        self.add_children([
            finalize_seq,
            capture_loose,
            position_for_pass,
        ])

    def setup(self, timeout: float) -> bool:
        """
        Registra chaves compartilhadas e delega setup aos filhos.

        :param timeout: tempo máximo sugerido pelo py_trees.
        """
        # (1) Blackboard para dados deste papel (se quiser chaves próprias)
        self._bb = self.attach_blackboard_client(name="support_bb_root")
        # Ex.: registrar base atual, se desejar compartilhar:
        self._bb.register_key("support_target", access=py_trees.common.Access.READ)

        # (2) Delegar setup aos filhos (boa prática para composites customizados)
        ok = True
        for c in self.children:
            # repassa um timeout pequeno; se um filho precisar de mais, trate nele
            ok = c.setup(timeout=timeout) and ok
        return ok
