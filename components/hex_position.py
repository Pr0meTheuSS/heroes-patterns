class HexPosition:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
