class Path:
    def __init__(self, steps, delay=0.5):
        self.steps = steps
        self.current_index = 0
        self.step_delay = delay
        self.step_timer = delay
