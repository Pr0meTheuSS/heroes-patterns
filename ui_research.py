import pygame
import pygame_gui

pygame.init()

# Размер окна
WIDTH, HEIGHT = 600, 400
window_surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пример UI: pygame_gui + кастом")

background = pygame.Surface((WIDTH, HEIGHT))
background.fill(pygame.Color('#222222'))

# Менеджер UI из pygame_gui
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Создаём кнопку pygame_gui
button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 50), (150, 50)),
                                      text='Нажми меня',
                                      manager=manager)

clock = pygame.time.Clock()

# Пример данных для миниатюр очередности ходов (просто цвета)
turn_order = [
    ("Игрок 1", pygame.Color('red')),
    ("Игрок 2", pygame.Color('blue')),
    ("Игрок 3", pygame.Color('green')),
]

def draw_turn_order(surface, order, pos=(350, 50), size=50, padding=10):
    """Рисуем миниатюры очередности ходов — цветные круги с подписями."""
    x, y = pos
    font = pygame.font.SysFont(None, 24)
    for i, (name, color) in enumerate(order):
        # Круг
        pygame.draw.circle(surface, color, (x + i*(size + padding) + size//2, y + size//2), size//2)
        # Подпись
        text_surf = font.render(name, True, pygame.Color('white'))
        text_rect = text_surf.get_rect(center=(x + i*(size + padding) + size//2, y + size + 15))
        surface.blit(text_surf, text_rect)

running = True
while running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обработка клика по кнопке pygame_gui
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == button:
                print("Кнопка нажата!")

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))

    # Рисуем миниатюры очередности ходов
    draw_turn_order(window_surface, turn_order)

    # Рендер UI pygame_gui
    manager.draw_ui(window_surface)

    pygame.display.update()

pygame.quit()
