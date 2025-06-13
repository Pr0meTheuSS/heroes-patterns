import pygame 
import pygame_gui
import os

from ecs import ECS
from components import (
    HexPosition, Hovered, Clickable, Renderable,
    Animation, Initiative, ActiveTurn, Path, BlockingMove,
    Health, Team, Attack, EndgameUI
)

from commands import AttackCommand

from hexmath import hex_to_pixel, pixel_to_hex, draw_hex
from systems import (
    animation_system, TurnManager, movement_system, 
    attack_system, command_system, endgame_system
) 
from pathfinding import bfs_with_fallback

# --- Константы ---
COLOR_BACKGROUND = (30, 30, 30)
COLOR_GRID_DEFAULT = (200, 200, 200)
COLOR_GRID_HOVERED = (255, 255, 100)
COLOR_GRID_ACTIVE_UNIT = (100, 200, 255)
COLOR_GRID_OUTLINE = (0, 0, 0)
COLOR_PATH_HOVER = (100, 255, 100)
COLOR_PATH_ACTIVE = (100, 255, 100)

TILE_SIZE = 30
GRID_RADIUS = 5
SCREEN_OFFSET_X = 400
SCREEN_OFFSET_Y = 300

# --- Вспомогательные функции ---

def is_passable(q, r, ecs):
    for entity in ecs.get_entities_with(HexPosition, BlockingMove):
        pos = ecs.get(HexPosition, entity)
        if pos.q == q and pos.r == r:
            return False
    return True

def draw_health_bar(surface, x, y, current, max_value, width=60, height=8):
    bg_color = (50, 50, 50)
    fg_color = (0, 200, 0)
    border_color = (255, 255, 255)
    text_color = (255, 255, 255)

    ratio = max(0, min(1, current / max_value))
    fg_width = int(width * ratio)

    pygame.draw.rect(surface, bg_color, (x, y, width, height))
    pygame.draw.rect(surface, fg_color, (x, y, fg_width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 1)

    font = pygame.font.SysFont(None, 16)
    text = font.render(f"{current}/{max_value}", True, text_color)
    text_rect = text.get_rect(center=(x + width // 2, y + height + 8))
    surface.blit(text, text_rect)

def render_entity(screen, entity, ecs):
    anim = ecs.get(Animation, entity)
    if anim:
        pos = ecs.get(HexPosition, entity)
        frame = anim.frames[anim.current_frame]
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        screen_x = x + SCREEN_OFFSET_X
        screen_y = y + SCREEN_OFFSET_Y
        team = ecs.get(Team, entity)

        if team and team.name == "player":
            base_color = (0, 200, 255)
        elif team and team.name == "computer":
            base_color = (255, 50, 50)
        else:
            base_color = (255, 255, 255)
        pygame.draw.circle(screen, base_color, (screen_x, screen_y), TILE_SIZE * 0.75)
        screen.blit(frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height()))

    health = ecs.get(Health, entity)
    if health:
        pos = ecs.get(HexPosition, entity)
        px, py = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        draw_health_bar(screen, px + SCREEN_OFFSET_X - 30, py + SCREEN_OFFSET_Y + 20, health.value, health.max_value)

def load_animation_frames(folder_path):
    return [
        pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
        for filename in sorted(os.listdir(folder_path)) if filename.endswith(".png")
    ]

# --- Инициализация игры и сущностей ---

def setup_entities(ecs):
    frames = load_animation_frames("assets/knight")

    knight = ecs.create_entity()
    ecs.add_component(knight, Animation(frames, frame_duration=0.15))
    ecs.add_component(knight, HexPosition(0, 0))
    ecs.add_component(knight, Initiative(5))
    ecs.add_component(knight, BlockingMove())
    ecs.add_component(knight, Health(100, 80))
    ecs.add_component(knight, Team("player"))
    ecs.add_component(knight, Attack(20))

    knight1 = ecs.create_entity()
    ecs.add_component(knight1, Animation(frames, frame_duration=0.15))
    ecs.add_component(knight1, HexPosition(-5, 0))
    ecs.add_component(knight1, Initiative(5))
    ecs.add_component(knight1, BlockingMove())
    ecs.add_component(knight1, Health(100, 1))
    ecs.add_component(knight1, Team("computer"))

    # Генерация сетки
    for q in range(-GRID_RADIUS, GRID_RADIUS + 1):
        for r in range(-GRID_RADIUS, GRID_RADIUS + 1):
            if abs(q + r) <= GRID_RADIUS:
                entity = ecs.create_entity()
                ecs.add_component(entity, HexPosition(q, r))
                ecs.add_component(entity, Renderable(COLOR_GRID_DEFAULT))
                ecs.add_component(entity, Clickable())

def draw_grid(screen, ecs):
    for entity in ecs.get_entities_with(HexPosition, Renderable):
        pos = ecs.get(HexPosition, entity)
        ren = ecs.get(Renderable, entity)
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        color = ren.color
        if ecs.get(Hovered, entity):
            color = COLOR_GRID_HOVERED
        if ecs.get(ActiveTurn, entity):
            color = COLOR_GRID_ACTIVE_UNIT
        draw_hex(screen, color, (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y), TILE_SIZE, 0)
        draw_hex(screen, COLOR_GRID_OUTLINE, (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y), TILE_SIZE, 2)

def update_hovered_tile(ecs, q, r):
    # Очистить прежний hovered
    for entity in ecs.get_entities_with(Hovered):
        ecs.components[Hovered].pop(entity)

    # Установить новый hovered
    for entity in ecs.get_entities_with(HexPosition, Clickable):
        pos = ecs.get(HexPosition, entity)
        if pos.q == q and pos.r == r:
            ecs.add_component(entity, Hovered())
            break

def handle_events(events, ecs, turn_manager, ui_manager, q, r):
    running = True
    active = turn_manager.get_active_unit()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        ui_manager.process_events(event)

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            for ent in ecs.get_entities_with(EndgameUI):
                ui = ecs.get(EndgameUI, ent)
                if event.ui_element == ui.window:
                    running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Атака по клику на вражеского юнита
            for entity in ecs.get_entities_with(HexPosition, Team):
                pos = ecs.get(HexPosition, entity)
                team = ecs.get(Team, entity)
                if pos.q == q and pos.r == r and active and team.name != ecs.get(Team, active).name:
                    ecs.add_component(active, AttackCommand(target_id=entity))

            # Построение пути для активного юнита
            if active and ecs.get(Path, active) is None:
                start = ecs.get(HexPosition, active)
                initiative = ecs.get(Initiative, active)
                path = bfs_with_fallback((start.q, start.r), (q, r), lambda q_, r_: is_passable(q_, r_, ecs))[:initiative.value - 1]
                if path:
                    ecs.add_component(active, Path(path[1:]))

    return running

def render_units(screen, ecs):
    for entity in ecs.get_entities_with(Animation, HexPosition):
        render_entity(screen, entity, ecs)

# --- Главный цикл ---

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    ui_manager = pygame_gui.UIManager((800, 600))

    ecs = ECS()
    setup_entities(ecs)

    turn_manager = TurnManager(ecs)
    turn_manager.start_battle()

    endgame_window = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        animation_system(ecs, dt)

        screen.fill(COLOR_BACKGROUND)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        q, r = pixel_to_hex(mouse_x - SCREEN_OFFSET_X, mouse_y - SCREEN_OFFSET_Y, TILE_SIZE)

        update_hovered_tile(ecs, q, r)

        active = turn_manager.get_active_unit()

        # Подсветка пути по наведению
        hovered_path = []
        if active and ecs.get(Path, active) is None and ecs.get(HexPosition, active):
            start_pos = ecs.get(HexPosition, active)
            initiative = ecs.get(Initiative, active)
            hovered_path = bfs_with_fallback((start_pos.q, start_pos.r), (q, r), lambda q_, r_: is_passable(q_, r_, ecs))[:initiative.value - 1]

        draw_grid(screen, ecs)

        for step in hovered_path:
            x, y = hex_to_pixel(step[0], step[1], TILE_SIZE)
            draw_hex(screen, COLOR_PATH_HOVER, (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y), TILE_SIZE, 0)

        render_units(screen, ecs)

        if active:
            path = ecs.get(Path, active)
            if path and path.current_index >= len(path.steps):
                ecs.components[Path].pop(active, None)
                turn_manager.end_turn()

        events = pygame.event.get()
        running = handle_events(events, ecs, turn_manager, ui_manager, q, r)

        command_system.command_system(ecs, lambda q_, r_: is_passable(q_, r_, ecs))
        movement_system.movement_system(ecs, dt)
        attack_system(ecs)
        ui_manager.update(dt)
        ui_manager.draw_ui(screen)

        endgame_system(ecs, ui_manager)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()

