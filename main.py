import pygame
import pygame_gui
import os

import colors

from ecs import ECS
from components import (
    HexPosition,
    Hovered,
    Clickable,
    Renderable,
    Animation,
    Initiative,
    ActiveTurn,
    Path,
    BlockingMove,
    Health,
    Team,
    Attack,
    EndgameUI,
)

from commands import AttackCommand

from hexmath import hex_to_pixel, pixel_to_hex, draw_hex
from systems import (
    animation_system,
    TurnManager,
    movement_system,
    attack_system,
    command_system,
    endgame_system,
)
from pathfinding import bfs_with_fallback

# --- Константы ---
TILE_SIZE = 30
MAP_WIDTH = 11
MAP_HEIGHT = 9
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_OFFSET_X = 0
SCREEN_OFFSET_Y = 0

# --- Вспомогательные функции ---


def compute_screen_offset():
    grid_pixel_width = TILE_SIZE * 3 / 2 * (MAP_WIDTH - 1) + TILE_SIZE
    grid_pixel_height = TILE_SIZE * (MAP_HEIGHT + 0.5)

    offset_x = (SCREEN_WIDTH - grid_pixel_width) // 2
    offset_y = (SCREEN_HEIGHT - grid_pixel_height) // 2
    return int(offset_x), int(offset_y)


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
        screen.blit(
            frame, (screen_x - frame.get_width() // 2, screen_y - frame.get_height())
        )

    health = ecs.get(Health, entity)
    if health:
        pos = ecs.get(HexPosition, entity)
        px, py = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        draw_health_bar(
            screen,
            px + SCREEN_OFFSET_X - 30,
            py + SCREEN_OFFSET_Y + 20,
            health.value,
            health.max_value,
        )


def load_animation_frames(folder_path):
    return [
        pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
        for filename in sorted(os.listdir(folder_path))
        if filename.endswith(".png")
    ]


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
    ecs.add_component(knight1, HexPosition(8, 0))
    ecs.add_component(knight1, Initiative(5))
    ecs.add_component(knight1, BlockingMove())
    ecs.add_component(knight1, Health(100, 1))
    ecs.add_component(knight1, Team("computer"))

    for r in range(MAP_HEIGHT):
        r_offset = r >> 1
        for q in range(-r_offset, MAP_WIDTH - r_offset):
            entity = ecs.create_entity()
            ecs.add_component(entity, HexPosition(q, r))
            ecs.add_component(entity, Renderable(colors.COLOR_GRID_DEFAULT))
            ecs.add_component(entity, Clickable())


def draw_grid(screen, ecs):
    for entity in ecs.get_entities_with(HexPosition, Renderable):
        pos = ecs.get(HexPosition, entity)
        ren = ecs.get(Renderable, entity)
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        color = ren.color
        if ecs.get(Hovered, entity):
            color = colors.COLOR_GRID_HOVERED
        if ecs.get(ActiveTurn, entity):
            color = colors.COLOR_GRID_ACTIVE_UNIT
        draw_hex(
            screen, color, (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y), TILE_SIZE, 0
        )
        draw_hex(
            screen,
            colors.COLOR_GRID_OUTLINE,
            (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y),
            TILE_SIZE,
            2,
        )


def update_hovered_tile(ecs, q, r):
    for entity in ecs.get_entities_with(Hovered):
        ecs.components[Hovered].pop(entity)

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
            for entity in ecs.get_entities_with(HexPosition, Team):
                pos = ecs.get(HexPosition, entity)
                team = ecs.get(Team, entity)
                if (
                    pos.q == q
                    and pos.r == r
                    and active
                    and team.name != ecs.get(Team, active).name
                ):
                    ecs.add_component(active, AttackCommand(target_id=entity))

            if active and ecs.get(Path, active) is None:
                start = ecs.get(HexPosition, active)
                initiative = ecs.get(Initiative, active)
                path = bfs_with_fallback(
                    (start.q, start.r), (q, r), lambda q_, r_: is_passable(q_, r_, ecs)
                )[: initiative.value - 1]
                if path:
                    ecs.add_component(active, Path(path[1:]))

    return running


def render_units(screen, ecs):
    for entity in ecs.get_entities_with(Animation, HexPosition):
        render_entity(screen, entity, ecs)


# --- Главный цикл ---


def game_loop():
    global SCREEN_OFFSET_X, SCREEN_OFFSET_Y

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

    SCREEN_OFFSET_X, SCREEN_OFFSET_Y = compute_screen_offset()

    ecs = ECS()
    setup_entities(ecs)

    turn_manager = TurnManager(ecs)
    turn_manager.start_battle()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        animation_system(ecs, dt)

        screen.fill(colors.COLOR_BACKGROUND)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        q, r = pixel_to_hex(
            mouse_x - SCREEN_OFFSET_X, mouse_y - SCREEN_OFFSET_Y, TILE_SIZE
        )

        update_hovered_tile(ecs, q, r)

        active = turn_manager.get_active_unit()

        hovered_path = []
        if active and ecs.get(Path, active) is None and ecs.get(HexPosition, active):
            start_pos = ecs.get(HexPosition, active)
            initiative = ecs.get(Initiative, active)
            hovered_path = bfs_with_fallback(
                (start_pos.q, start_pos.r),
                (q, r),
                lambda q_, r_: is_passable(q_, r_, ecs),
            )[: initiative.value - 1]

        draw_grid(screen, ecs)

        for step in hovered_path:
            x, y = hex_to_pixel(step[0], step[1], TILE_SIZE)
            draw_hex(
                screen,
                colors.COLOR_PATH_HOVER,
                (x + SCREEN_OFFSET_X, y + SCREEN_OFFSET_Y),
                TILE_SIZE,
                0,
            )

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
