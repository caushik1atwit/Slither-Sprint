"""
Apple model - represents collectible apples
"""


class Apple:
    """Represents a collectible apple (red or golden)"""

    def __init__(self, x: int, y: int, is_golden: bool = False):
        self.x = x
        self.y = y
        self.is_golden = is_golden

    @property
    def position(self):
        """Get the (x, y) position tuple"""
        return (self.x, self.y)
