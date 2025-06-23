from dataclasses import dataclass


@dataclass
class Attack:
    power: int
    range: int = 1  # дальность атаки (0 — только соседние клетки)
