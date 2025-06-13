from components import Health, Initiative, ActiveTurn

class TurnManager:
    def __init__(self, ecs):
        self.ecs = ecs
        self.turn_queue = []

    def is_alive(self, entity):
        return self.ecs.has(Health, entity) and self.ecs.get(Health, entity).value > 0

    def start_battle(self):
        units = self.ecs.get_entities_with(Initiative)
        alive_units = [e for e in units if self.is_alive(e)]
        sorted_units = sorted(alive_units, key=lambda e: -self.ecs.get(Initiative, e).value)
        self.turn_queue = sorted_units

        if self.turn_queue:
            self.ecs.add_component(self.turn_queue[0], ActiveTurn())

    def end_turn(self):
        while self.turn_queue:
            current = self.turn_queue.pop(0)
            self.ecs.remove_component(current, ActiveTurn)

            if self.is_alive(current):
                self.turn_queue.append(current)

            next_unit = self.get_active_unit()
            if next_unit is not None:
                self.ecs.add_component(next_unit, ActiveTurn())
                return

        print("Нет живых юнитов — конец боя?")

    def get_active_unit(self):
        while self.turn_queue:
            active = self.turn_queue[0]
            if self.is_alive(active):
                return active
            else:
                # Убираем мёртвого юнита
                self.turn_queue.pop(0)
        return None  # Все мертвы

