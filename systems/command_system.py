from pathfinding import bfs_with_fallback, hex_distance

from commands import AttackCommand, QueuedAttack
from components import HexPosition, Attack, Initiative, Path


def command_system(ecs, is_passable):
    for entity in ecs.get_entities_with(AttackCommand):
        cmd = ecs.get(AttackCommand, entity)
        target = cmd.target_id

        if not ecs.has(HexPosition, entity) or not ecs.has(HexPosition, target):
            ecs.remove_component(entity, AttackCommand)
            continue

        attacker_pos = ecs.get(HexPosition, entity)
        target_pos = ecs.get(HexPosition, target)

        atk = ecs.get(Attack, entity)
        initiative = ecs.get(Initiative, entity).value

        distance = hex_distance(
            (attacker_pos.q, attacker_pos.r), (target_pos.q, target_pos.r)
        )

        print("distance:", distance)

        if distance <= atk.range:
            ecs.add_component(entity, QueuedAttack(target))
        elif distance <= initiative + 1:
            path = bfs_with_fallback(
                (attacker_pos.q, attacker_pos.r),
                (target_pos.q, target_pos.r),
                is_passable,
            )[:initiative]
            if len(path) <= initiative:
                print("QueuedAttack push")
                ecs.add_component(entity, Path(path[1:]))
                ecs.add_component(entity, QueuedAttack(target))

        ecs.remove_component(entity, AttackCommand)
