from dataclasses import dataclass

@dataclass
class Health:
    def __init__(self, max_value, value):
        self.max_value = max_value
        self.value = value

