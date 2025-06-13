import pygame_gui
import pygame

from components import GameOver, EndgameUI, Health, Team

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
