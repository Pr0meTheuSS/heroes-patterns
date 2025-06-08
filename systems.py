import pygame
import pygame_gui
from components import Animation, HexPosition, Path, Initiative, Health, ActiveTurn, QueuedAttack, AttackCommand, Attack
from components import Health, Team, GameOver

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
            ecs.remove_component(entity, Path)

from pathfinding import bfs_with_fallback, hex_distance
from utils import adjacent

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

        distance = hex_distance((attacker_pos.q, attacker_pos.r), (target_pos.q, target_pos.r))

        if distance <= atk.range:
            ecs.add_component(entity, QueuedAttack(target))
        elif distance <= initiative:
            path = bfs_with_fallback((attacker_pos.q, attacker_pos.r), (target_pos.q, target_pos.r), is_passable)[:(initiative-1)]
            if len(path) - 1 <= initiative:
                print("QueuedAttack push")
                ecs.add_component(entity, Path(path[1:]))
                ecs.add_component(entity, QueuedAttack(target))

        ecs.remove_component(entity, AttackCommand)

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

import pygame
import pygame_gui
from components import Health, Team, GameOver, EndgameUI  # не забудь импортировать

def endgame_system(ecs, ui_manager):
    if ecs.get_entities_with(GameOver, EndgameUI):
        return  # уже вызвано

    teams_alive = set()
    for ent in ecs.get_entities_with(Health, Team):
        hp = ecs.get(Health, ent).value
        if hp > 0:
            teams_alive.add(ecs.get(Team, ent).name)

    if len(teams_alive) <= 1:
        winner = teams_alive.pop() if teams_alive else None
        if winner == "player":
            msg = "<b>Победа!</b><br>Вы победили всех врагов."
        else:
            msg = "<b>Поражение</b><br>Все ваши юниты уничтожены."

        window = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(200, 150, 400, 200),
            html_message=msg,
            manager=ui_manager,
            window_title="Игра окончена"
        )

        marker = ecs.create_entity()
        ecs.add_component(marker, GameOver())
        ecs.add_component(marker, EndgameUI(window))
