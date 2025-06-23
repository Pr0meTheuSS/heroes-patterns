from components import HexPosition, Path


def movement_system(ecs, dt):
    for entity in ecs.get_entities_with(HexPosition, Path):
        pos = ecs.get(HexPosition, entity)
        path = ecs.get(Path, entity)

        if path.current_index < len(path.steps):
            path.step_timer -= dt
            if path.step_timer <= 0:
                target_q, target_r = path.steps[path.current_index]
                pos.q, pos.r = target_q, target_r
                path.current_index += 1
                path.step_timer = path.step_delay
        else:
            ecs.remove_component(entity, Path)
