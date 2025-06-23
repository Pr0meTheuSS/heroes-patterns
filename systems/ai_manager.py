from components import AiManagable
from components import Team
from components import HexPosition
from components import Initiative
from components import Path
from pathfinding import bfs_with_fallback
from pathfinding import is_passable


def ai_managment(ecs, turn_manager):
    for entity in ecs.get_entities_with(AiManagable):
        active = turn_manager.get_active_unit()
        if active and ecs.get(Team, active).name != "player":
            print("Handle ai managnent for entity", entity)
            start = ecs.get(HexPosition, active)
            initiative = ecs.get(Initiative, active)
            path = bfs_with_fallback(
                (start.q, start.r),
                (5, 5),
                lambda q_, r_: is_passable(q_, r_, ecs),
            )[: initiative.value + 1]
            if path:
                ecs.add_component(active, Path(path[1:]))

            turn_manager.end_turn()
        # TODO: make decidion
        # Add turn to queue
