"""
Snake model - represents a player's snake
"""

import pygame
from model.pane import Pane
from model.power_up import PowerUpType
from config import (
    SNAKE_LEN,
    STEP_MS,
    SPEED_BOOST_DURATION,
    INVINCIBILITY_DURATION,
    APPLES_FOR_SPEED_BOOST,
)


class Snake:
    """Represents a player's snake with movement and power-up logic"""

    def __init__(self, pane: Pane, x: int, y: int, body_col, head_col, name: str):
        self.pane = pane
        self.body = [(x, y + i) for i in range(SNAKE_LEN)]
        self.dx, self.dy = 0, -1
        self.body_col = body_col
        self.head_col = head_col
        self.name = name
        self.alive = True
        self.steps = 0
        self.apples_collected = 0
        self.active_powerup = PowerUpType.NONE
        self.powerup_end_time = 0
        self.base_step_ms = STEP_MS
        self.current_step_ms = STEP_MS

    @property
    def head(self):
        """Get the head position of the snake"""
        return self.body[0]

    def steer(self, left: bool, right: bool):
        """
        Update steering direction

        Args:
            left: True if steering left
            right: True if steering right
        """
        if left:
            self.dx = -1
        elif right:
            self.dx = 1

    def collect_apple(self):
        """Collect a red apple and check for speed boost"""
        self.apples_collected += 1
        if self.apples_collected % APPLES_FOR_SPEED_BOOST == 0:
            self.activate_powerup(PowerUpType.SPEED_BOOST)

    def collect_golden_apple(self):
        """Collect a golden apple for invincibility"""
        self.activate_powerup(PowerUpType.INVINCIBILITY)

    def activate_powerup(self, powerup_type: PowerUpType):
        """
        Activate a power-up

        Args:
            powerup_type: Type of power-up to activate
        """
        current_time = pygame.time.get_ticks()
        self.active_powerup = powerup_type

        if powerup_type == PowerUpType.SPEED_BOOST:
            self.powerup_end_time = current_time + SPEED_BOOST_DURATION
            self.current_step_ms = int(self.base_step_ms * 0.7)  # 30% faster
        elif powerup_type == PowerUpType.INVINCIBILITY:
            self.powerup_end_time = current_time + INVINCIBILITY_DURATION
            self.current_step_ms = self.base_step_ms
        else:
            self.powerup_end_time = 0
            self.current_step_ms = self.base_step_ms

    def update_powerups(self):
        """Check if power-ups have expired"""
        if self.active_powerup != PowerUpType.NONE:
            if pygame.time.get_ticks() >= self.powerup_end_time:
                self.active_powerup = PowerUpType.NONE
                self.current_step_ms = self.base_step_ms

    def is_invincible(self):
        """Check if snake is currently invincible"""
        return self.active_powerup == PowerUpType.INVINCIBILITY

    def step(self):
        """Move the snake forward one step"""
        if not self.alive:
            return

        self.steps += 1
        hx, hy = self.head
        nx, ny = hx + self.dx, hy + self.dy

        # Check boundary collision
        if not self.pane.inside(nx, ny):
            self.alive = False
            return

        # Move snake
        self.body.insert(0, (nx, ny))
        while len(self.body) > SNAKE_LEN:
            self.body.pop()

        # Check self-collision
        if self.head in self.body[1:]:
            self.alive = False
