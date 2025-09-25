import py_trees
from ..defender.defender_conditions import (
    Ball_in_defensive_area,
    Opponent_in_danger_zone,
    Opponent_has_ball_in_danger_zone,
    Ball_moving_towards_goal,
)
from ..defender.defender_actions import DefenderActions
from Behaviour_tree.core.World_State import RobotID
from Behaviour_tree.core.blackboard import Blackboard_Manager


class DefenderTree:
    """
    Árvore de comportamento para o defensor.
    """

    def __init__(self, robot_id: RobotID):
        self.robot_id = robot_id
        self.blackboard = Blackboard_Manager.get_instance()
        self.defender_actions = DefenderActions(name="DefenderActions", blackboard=self.blackboard)

    def create_tree(self) -> py_trees.behaviour.Behaviour:
        """
        Cria a árvore de comportamento do defensor.
        """

        # ---------------------------------------------------------------------#
        #                          CONDIÇÕES                                   #
        # ---------------------------------------------------------------------#

        ball_in_defensive_area = Ball_in_defensive_area(name="Ball in Defensive Area")
        opponent_in_danger_zone = Opponent_in_danger_zone(name="Opponent in Danger Zone")
        opponent_has_ball_in_danger_zone = Opponent_has_ball_in_danger_zone(name="Opponent Has Ball in Danger Zone")
        ball_moving_towards_goal = Ball_moving_towards_goal(name="Ball Moving Towards Goal")

        # ---------------------------------------------------------------------#
        #                          AÇÕES                                       #
        # ---------------------------------------------------------------------#

        set_defensive_position = py_trees.behaviours.Success(
            name="Set Defensive Position",
            action=lambda: self.defender_actions.set_defensive_position(self.robot_id),
        )
        intercept_ball = py_trees.behaviours.Success(
            name="Intercept Ball",
            action=lambda: self.defender_actions.intercept_ball(self.robot_id),
        )

        # ---------------------------------------------------------------------#
        #                          RAMOS                                       #
        # ---------------------------------------------------------------------#

        # Ramo: Interceptar a bola se ela estiver se movendo em direção ao gol
        intercept_ball_branch = py_trees.composites.Sequence(
            name="Intercept Ball Branch",
            memory=False,
            children=[ball_moving_towards_goal, intercept_ball],
        )

        # Ramo: Bloquear o oponente se ele estiver na zona perigosa com a bola
        block_opponent_branch = py_trees.composites.Sequence(
            name="Block Opponent Branch",
            memory=False,
            children=[opponent_has_ball_in_danger_zone, set_defensive_position],
        )

        # Ramo: Proteger a área defensiva se a bola estiver na área defensiva
        protect_area_branch = py_trees.composites.Sequence(
            name="Protect Area Branch",
            memory=False,
            children=[ball_in_defensive_area, set_defensive_position],
        )

        # Ramo: Monitorar oponente na zona perigosa
        monitor_opponent_branch = py_trees.composites.Sequence(
            name="Monitor Opponent Branch",
            memory=False,
            children=[opponent_in_danger_zone, set_defensive_position],
        )

        # ---------------------------------------------------------------------#
        #                          NÓ RAIZ                                     #
        # ---------------------------------------------------------------------#

        # O nó raiz escolhe entre os ramos de interceptação, bloqueio ou proteção
        root = py_trees.composites.Selector(
            name="Defender Root",
            memory=False,
            children=[
                intercept_ball_branch,
                block_opponent_branch,
                protect_area_branch,
                monitor_opponent_branch,
            ],
        )

        return root


if __name__ == "__main__":
    import py_trees.display

    robot_id = RobotID.Defender
    defender_tree = DefenderTree(robot_id=robot_id)

    tree = defender_tree.create_tree()

    print("\n=== ESTRUTURA EM ASCII ===")
    print(py_trees.display.unicode_tree(tree))

    try:
        py_trees.display.render_dot_tree(tree, name="defender_tree")
        print(
            "\nArquivo DOT gerado como 'defender_tree.dot' e imagem PNG correspondente."
        )
    except Exception as e:
        print(f"Não foi possível gerar DOT/PNG: {e}")