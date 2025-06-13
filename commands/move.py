from dataclasses import dataclass

@dataclass
class MoveCommand:
    path: list  # список клеток [(q, r), ...]

