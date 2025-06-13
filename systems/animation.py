from components.animation import Animation

def animation_system(ecs, dt):
    for entity in ecs.get_entities_with(Animation):
        anim = ecs.get(Animation, entity)
        anim.update(dt)
