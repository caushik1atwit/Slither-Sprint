"""
Obstacles model - manages obstacle blocks
"""


class Obstacles:
    """Manages obstacle blocks in the game world"""

    def __init__(self):
        self.blocks = set()

    def add(self, x: int, y: int):
        """
        Add an obstacle block at position

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.blocks.add((x, y))

    def collides(self, pos: tuple) -> bool:
        """
        Check if position collides with an obstacle

        Args:
            pos: (x, y) tuple to check

        Returns:
            True if collision detected
        """
        return pos in self.blocks

    def cleanup(self, screen_bottom: int):
        """
        Remove obstacles that are off-screen

        Args:
            screen_bottom: Y coordinate of screen bottom
        """
        self.blocks = {(x, y) for x, y in self.blocks if y < screen_bottom}
