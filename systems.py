import pygame
from components import Animation, HexPosition, Path, Initiative, ActiveTurn

def animation_system(ecs, dt):
    for entity in ecs.get_entities_with(Animation):
        anim = ecs.get(Animation, entity)
        anim.update(dt)

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
            ecs.components[Path].pop(entity)

class TurnManager:
    def __init__(self, ecs):
        self.ecs = ecs
        self.turn_queue = []

    def start_battle(self):
        units = self.ecs.get_entities_with(Initiative)
        sorted_units = sorted(units, key=lambda e: -self.ecs.get(Initiative, e).value)
        self.turn_queue = sorted_units

        if self.turn_queue:
            self.ecs.add_component(self.turn_queue[0], ActiveTurn())

    def end_turn(self):
        if not self.turn_queue:
            return

        current = self.turn_queue.pop(0)
        if self.ecs.has(ActiveTurn, current):
            self.ecs.components[ActiveTurn].pop(current)

        self.turn_queue.append(current)
        self.ecs.add_component(self.turn_queue[0], ActiveTurn())

    def get_active_unit(self):
        return self.turn_queue[0] if self.turn_queue else None
