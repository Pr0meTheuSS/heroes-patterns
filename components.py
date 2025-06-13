class HexPosition:
    def __init__(self, q, r):
        self.q = q
        self.r = r

class Hovered:
    pass

class Clickable:
    pass

class Renderable:
    def __init__(self, color):
        self.color = color

from dataclasses import dataclass
import pygame

@dataclass
class Animation:
    frames: list[pygame.Surface]
    frame_duration: float
    loop: bool = True
    current_time: float = 0.0
    current_frame: int = 0

    def update(self, dt: float):
        self.current_time += dt
        if self.current_time >= self.frame_duration:
            self.current_time -= self.frame_duration
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1

class Path:
    def __init__(self, steps, delay=0.5):
        self.steps = steps
        self.current_index = 0
        self.step_delay = delay
        self.step_timer = delay

@dataclass
class Initiative:
    value: int

@dataclass
class ActiveTurn:
    pass

@dataclass
class BlockingMove:
    pass

@dataclass
class Health:
    def __init__(self, max_value, value):
        self.max_value = max_value
        self.value = value

@dataclass
class Team:
    def __init__(self, name):
        self.name = name

# components.py (добавь или проверь наличие)
from dataclasses import dataclass

@dataclass
class MoveCommand:
    path: list  # список клеток [(q, r), ...]

@dataclass
class AttackCommand:
    target_id: int  # цель для атаки

@dataclass
class QueuedAttack:
    target_id: int  # цель для отложенной атаки

@dataclass
class Attack:
    power: int
    range: int = 1  # дальность атаки (0 — только соседние клетки)

@dataclass
class Path:
    steps: list
    current_index: int = 0
    step_timer: float = 0.0
    step_delay: float = 0.2
