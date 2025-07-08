from pygame import Surface
from dataclasses import dataclass

states = ["idle", "walk", "attack", "hurt", "dead"]


@dataclass
class Animation:
    animations: dict[str, list[Surface]]
    frame_duration: float
    current_time: float = 0.0
    current_frame: int = 0
    current_state: str = "idle"
    queued_state: str = ""

    def update(self, dt: float):
        self.current_time += dt
        frames = self.animations[self.current_state]

        if self.current_time >= self.frame_duration:
            self.current_time -= self.frame_duration
            self.current_frame += 1

            if self.current_frame >= len(frames):
                if self.is_looping():
                    self.current_frame = 0
                else:
                    self.current_frame = len(frames) - 1
                    if self.current_state != "dead":
                        self.set_state("idle")

        if self.queued_state != "":
            self.current_state = self.queued_state
            self.queued_state = ""

    def get_frames(self) -> list[Surface]:
        return self.animations[self.current_state]

    def get_current_frame(self) -> Surface:
        return self.animations[self.current_state][self.current_frame]

    def set_state(self, new_state: str):
        frames = self.animations[self.current_state]

        if self.current_frame != len(frames) - 1:
            self.queued_state = new_state
        if new_state != self.current_state:
            self.current_state = new_state
            self.current_frame = 0
            self.current_time = 0.0

    def is_looping(self):
        return self.current_state in ["walk", "idle"]
