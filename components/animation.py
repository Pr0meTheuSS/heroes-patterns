from pygame import Surface
from dataclasses import dataclass


@dataclass
class Animation:
    animations: dict[str, list[Surface]]
    frame_duration: float
    loop: bool = True
    current_time: float = 0.0
    current_frame: int = 0
    current_state: str = "idle"

    def update(self, dt: float):
        self.current_time += dt
        frames = self.animations[self.current_state]

        if self.current_time >= self.frame_duration:
            self.current_time -= self.frame_duration
            self.current_frame += 1

            if self.current_frame >= len(frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(frames) - 1

    def get_frames(self) -> list[Surface]:
        return self.animations[self.current_state]

    def get_current_frame(self) -> Surface:
        return self.animations[self.current_state][self.current_frame]

    def set_state(self, new_state: str):
        if new_state != self.current_state:
            self.current_state = new_state
            self.current_frame = 0
            self.current_time = 0.0
