class point:
    def __init__(self, x=0, y=0):
        if (type(x) is list):
            x, y = x
        self.x = x
        self.y = y

    def __add__(self, other):
        return point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return point(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return "(%d, %d)" % ((self.x), (self.y))
