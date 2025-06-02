import pygame
from ecs import ECS
from components import HexPosition, Hovered, Clickable, Renderable, Animation
from hexmath import hex_to_pixel, pixel_to_hex, draw_hex
from systems import animation_system
import os

from pathfinding import bfs
from components import Path
from systems import movement_system

hovered_path = []

def render_entity(screen, entity, ecs):
    anim = ecs.get(Animation, entity)
    if anim:
        pos = ecs.get(HexPosition, entity)
        frame = anim.frames[anim.current_frame]
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        screen.blit(frame, (x + 400 - frame.get_width()//2, y + 300 - frame.get_height()))

def load_animation_frames(folder_path):
    frames = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png"):
            img = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
            frames.append(img)
    return frames

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

ecs = ECS()
TILE_SIZE = 30
GRID_RADIUS = 5

frames = load_animation_frames("assets/knight")
knight = ecs.create_entity()
ecs.add_component(knight, Animation(frames, frame_duration=0.15))
ecs.add_component(knight, HexPosition(0, 0))

for q in range(-GRID_RADIUS, GRID_RADIUS+1):
    for r in range(-GRID_RADIUS, GRID_RADIUS+1):
        if abs(q + r) <= GRID_RADIUS:
            entity = ecs.create_entity()
            ecs.add_component(entity, HexPosition(q, r))
            ecs.add_component(entity, Renderable((200, 200, 200)))
            ecs.add_component(entity, Clickable())

running = True

while running:
    dt = clock.tick(60) / 1000.0

    animation_system(ecs, dt)
    movement_system(ecs, dt)

    screen.fill((30, 30, 30))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for entity in ecs.get_entities_with(Hovered):
        ecs.components[Hovered].pop(entity)

    q, r = pixel_to_hex(mouse_x - 400, mouse_y - 300, TILE_SIZE)
    # маршрут до наведённой клетки
    start_pos = ecs.get(HexPosition, knight)
    hovered_path = bfs(
        (start_pos.q, start_pos.r),
        (q, r),
        lambda q, r: True  # пока проходимо всё
    )

    for entity in ecs.get_entities_with(HexPosition, Clickable):
        pos = ecs.get(HexPosition, entity)
        if pos.q == q and pos.r == r:
            ecs.add_component(entity, Hovered())
            break

    for entity in ecs.get_entities_with(HexPosition, Renderable):
        pos = ecs.get(HexPosition, entity)
        ren = ecs.get(Renderable, entity)
        x, y = hex_to_pixel(pos.q, pos.r, TILE_SIZE)
        color = ren.color
        if ecs.get(Hovered, entity):
            color = (255, 255, 100)
        draw_hex(screen, color, (x + 400, y + 300), TILE_SIZE, 0)
        draw_hex(screen, (0, 0, 0), (x + 400, y + 300), TILE_SIZE, 2)
        # отрисуем путь
        path = ecs.get(Path, knight)
        if path:
            for step in path.steps[path.current_index:]:
                x, y = hex_to_pixel(step[0], step[1], TILE_SIZE)
                draw_hex(screen, (100, 255, 100), (x + 400, y + 300), TILE_SIZE, 0)

    for step in hovered_path:
        x, y = hex_to_pixel(step[0], step[1], TILE_SIZE)
        draw_hex(screen, (100, 255, 100), (x + 400, y + 300), TILE_SIZE, 0)

    render_entity(screen, knight, ecs)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                path = bfs(
                    (ecs.get(HexPosition, knight).q, ecs.get(HexPosition, knight).r),
                    (q, r),
                    lambda q, r: True
                )
                if path:
                    ecs.add_component(knight, Path(path[1:]))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
