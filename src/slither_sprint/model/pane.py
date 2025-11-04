"""
Pane model - represents a player's game area
"""

import random
from dataclasses import dataclass


@dataclass
class Pane:
    """Represents a vertical pane/column range for a player"""

    x0: int
    x1: int

    def inside(self, x: int, y: int = None) -> bool:
        """Check if x coordinate is within this pane"""
        return self.x0 <= x <= self.x1

    def rand_x(self) -> int:
        """Get a random x coordinate within this pane"""
        return random.randint(self.x0, self.x1)

    def get_empty_cell(self, occupied_positions, y_min, y_max):
        """
        Find a random empty cell in this pane

        Args:
            occupied_positions: Set of (x, y) tuples that are occupied
            y_min: Minimum y coordinate
            y_max: Maximum y coordinate

        Returns:
            (x, y) tuple or None if no empty cell found
        """
        attempts = 0
        while attempts < 50:
            x = self.rand_x()
            y = random.randint(y_min, y_max)
            if (x, y) not in occupied_positions:
                return (x, y)
            attempts += 1
        return None
