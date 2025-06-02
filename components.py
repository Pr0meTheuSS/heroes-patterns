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
    value: int  # приоритет хода, выше — раньше

@dataclass
class ActiveTurn:
    pass  # просто маркер, указывает на активного юнита
