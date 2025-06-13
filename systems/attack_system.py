from commands import QueuedAttack 
from components import Attack, HexPosition, Path, Health
from pathfinding import hex_distance

def attack_system(ecs):
    for entity in ecs.get_entities_with(QueuedAttack, Attack, HexPosition):
        if ecs.has(Path, entity):
            continue  # Сначала пусть дойдёт по пути

        queued = ecs.get(QueuedAttack, entity)
        target = queued.target_id

        if not ecs.has(HexPosition, target) or not ecs.has(Health, target):
            ecs.remove_component(entity, QueuedAttack)
            continue

        attacker_pos = ecs.get(HexPosition, entity)
        target_pos = ecs.get(HexPosition, target)
        atk = ecs.get(Attack, entity)

        distance = hex_distance((attacker_pos.q, attacker_pos.r), (target_pos.q, target_pos.r))

        if distance <= atk.range:
            ecs.get(Health, target).value -= atk.power
            print(f"{entity} атакует {target} на {atk.power} урона")
            if ecs.get(Health, target).value <= 0:
                ecs.delete_entity(target)
        else:
            print(f"{entity} слишком далеко от {target} — атака отменена")

        ecs.remove_component(entity, QueuedAttack)

