import pygame
import os
from ecs import ECS
from components import (
    HexPosition, Hovered, Clickable, Renderable,
    Animation, Initiative, ActiveTurn, Path
)
from hexmath import hex_to_pixel, pixel_to_hex, draw_hex
from systems import animation_system, TurnManager, movement_system
from pathfinding import bfs

# --- Цветовые константы ---
COLOR_BACKGROUND = (30, 30, 30)
COLOR_GRID_DEFAULT = (200, 200, 200)
COLOR_GRID_HOVERED = (255, 255, 100)
COLOR_GRID_ACTIVE_UNIT = (100, 200, 255)
COLOR_GRID_OUTLINE = (0, 0, 0)
COLOR_PATH_HOVER = (100, 255, 100)
COLOR_PATH_ACTIVE = (100, 255, 100)

def render_entity(screen, entity, ecs):
    anim = ecs.get(Animation, entity)
    if anim:
        pos = ecs.get(HexPosition, entity)
        frame = anim.frames[anim.current_frame]
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        screen.blit(frame, (x + 400 - frame.get_width() // 2, y + 300 - frame.get_height()))

def load_animation_frames(folder_path):
    return [
        pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
        for filename in sorted(os.listdir(folder_path)) if filename.endswith(".png")
    ]

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

ecs = ECS()
TILE_SIZE = 30
GRID_RADIUS = 5
turn_manager = TurnManager(ecs)

frames = load_animation_frames("assets/knight")

# --- Юниты ---
knight = ecs.create_entity()
ecs.add_component(knight, Animation(frames, frame_duration=0.15))
ecs.add_component(knight, HexPosition(0, 0))
ecs.add_component(knight, Initiative(5))

knight1 = ecs.create_entity()
ecs.add_component(knight1, Animation(frames, frame_duration=0.15))
ecs.add_component(knight1, HexPosition(-3, 0))
ecs.add_component(knight1, Initiative(5))

knight2 = ecs.create_entity()
ecs.add_component(knight2, Animation(frames, frame_duration=0.15))
ecs.add_component(knight2, HexPosition(3, 0))
ecs.add_component(knight2, Initiative(3))

turn_manager.start_battle()

# --- Генерация сетки ---
for q in range(-GRID_RADIUS, GRID_RADIUS + 1):
    for r in range(-GRID_RADIUS, GRID_RADIUS + 1):
        if abs(q + r) <= GRID_RADIUS:
            entity = ecs.create_entity()
            ecs.add_component(entity, HexPosition(q, r))
            ecs.add_component(entity, Renderable(COLOR_GRID_DEFAULT))
            ecs.add_component(entity, Clickable())

# --- Игровой цикл ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    animation_system(ecs, dt)
    movement_system(ecs, dt)
    screen.fill(COLOR_BACKGROUND)

    mouse_x, mouse_y = pygame.mouse.get_pos()
    q, r = pixel_to_hex(mouse_x - 400, mouse_y - 300, TILE_SIZE)

    # Обновляем hovered
    for entity in ecs.get_entities_with(Hovered):
        ecs.components[Hovered].pop(entity)

    for entity in ecs.get_entities_with(HexPosition, Clickable):
        pos = ecs.get(HexPosition, entity)
        if pos.q == q and pos.r == r:
            ecs.add_component(entity, Hovered())
            break

    # Активный юнит
    active = turn_manager.get_active_unit()

    # Подсветка пути до клетки под курсором
    hovered_path = []
    if active and ecs.get(Path, active) is None and ecs.get(HexPosition, active):
        start_pos = ecs.get(HexPosition, active)
        initiative = ecs.get(Initiative, active)
        hovered_path = bfs((start_pos.q, start_pos.r), (q, r), lambda q, r: True)[:(initiative.value-1)]

    # Отрисовка сетки
    for entity in ecs.get_entities_with(HexPosition, Renderable):
        pos = ecs.get(HexPosition, entity)
        ren = ecs.get(Renderable, entity)
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)

        color = ren.color
        if ecs.get(Hovered, entity):
            color = COLOR_GRID_HOVERED
        if ecs.get(ActiveTurn, entity):
            color = COLOR_GRID_ACTIVE_UNIT

        draw_hex(screen, color, (x + 400, y + 300), TILE_SIZE, 0)
        draw_hex(screen, COLOR_GRID_OUTLINE, (x + 400, y + 300), TILE_SIZE, 2)

    # Подсветка возможного пути по наведению
    for step in hovered_path:
        x, y = hex_to_pixel(step[0], step[1], TILE_SIZE)
        draw_hex(screen, COLOR_PATH_HOVER, (x + 400, y + 300), TILE_SIZE, 0)

    # Отрисовка юнитов
    for entity in ecs.get_entities_with(Animation, HexPosition):
        render_entity(screen, entity, ecs)

    # Проверка конца хода — если путь есть и завершён
    if active:
        path = ecs.get(Path, active)
        if path and path.current_index >= len(path.steps):
            ecs.components[Path].pop(active, None)
            turn_manager.end_turn()
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if active and ecs.get(Path, active) is None:
                start = ecs.get(HexPosition, active)
                initiative = ecs.get(Initiative, active)
                path = bfs((start.q, start.r), (q, r), lambda q, r: True)[:(initiative.value-1)]
                if path:
                    ecs.add_component(active, Path(path[1:]))

    pygame.display.flip()

pygame.quit()
