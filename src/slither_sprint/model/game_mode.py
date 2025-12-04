"""
Game mode enumeration
"""

from enum import Enum


class GameMode(Enum):
    """Game states for menu, playing, and paused"""

    MENU = 0
    PLAYING = 1
    PAUSED = 2
