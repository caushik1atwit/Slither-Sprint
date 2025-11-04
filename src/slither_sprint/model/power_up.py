"""
Power-up types enumeration
"""

from enum import Enum


class PowerUpType(Enum):
    """Types of power-ups available in the game"""

    NONE = 0
    SPEED_BOOST = 1
    INVINCIBILITY = 2
