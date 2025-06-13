from pygame import Surface
from dataclasses import dataclass

@dataclass
class Animation:
    frames: list[Surface]
    frame_duration: float
    loop: bool = True
    current_time: float = 0.0
    current_frame: int = 0
    # TODO: think about move behaivor to system ???
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
