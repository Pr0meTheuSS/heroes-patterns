from components import AiManagable
from components import Team
from components import HexPosition
from components import Initiative
from components import Path
from commands import AttackCommand
from components import Animation
from pathfinding import bfs_with_fallback
from pathfinding import is_passable


def ai_managment(ecs, turn_manager):
    for entity in ecs.get_entities_with(AiManagable):
        active = turn_manager.get_active_unit()
        path = ecs.get(Path, active)
        if active and ecs.get(Team, active).name != "player":
            if (
                path
                and path.current_index >= len(path.steps)
                and not ecs.get(AttackCommand, active)
            ):
                ecs.components[Path].pop(active, None)
                print("end turn")
                ecs.get(Animation, active).set_state("idle")
                turn_manager.end_turn()
                return
            if path is None:
                start = ecs.get(HexPosition, active)
                initiative = ecs.get(Initiative, active)
                path = bfs_with_fallback(
                    (start.q, start.r),
                    (5, 5),
                    lambda q_, r_: is_passable(q_, r_, ecs),
                )[: initiative.value + 1]
                if path:
                    ecs.add_component(active, Path(path[1:]))
                path = ecs.get(Path, active)
                print(path.current_index, len(path.steps))

        # TODO: make decidion
        # Add turn to queue
