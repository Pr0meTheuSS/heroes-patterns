from dataclasses import dataclass


@dataclass
class UnitState:
    def __init__(self, state) -> None:
        self.state = state
