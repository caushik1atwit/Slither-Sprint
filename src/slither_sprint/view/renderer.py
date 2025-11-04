"""
Renderer - handles all drawing operations
"""

import pygame
from config import (
    WIDTH,
    HEIGHT,
    CELL,
    GRID_H,
    PANE_COLS,
    BG_COLOR,
    DIVIDER_COLOR,
    TEXT_COLOR,
    PADDING,
    RED_APPLE_COLOR,
    GOLDEN_APPLE_COLOR,
    OBSTACLE_A,
    OBSTACLE_B,
    FINISH_LINE_COLOR,
    P1_HEAD,
    P2_HEAD,
)
from model.power_up import PowerUpType


class Renderer:
    """Handles all rendering operations"""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 18)

        # Create clip rectangles for split screen
        self.clip_p1 = pygame.Rect(0, 0, PANE_COLS * CELL, HEIGHT)
        self.clip_p2 = pygame.Rect(PANE_COLS * CELL, 0, PANE_COLS * CELL, HEIGHT)

    def render(self, game_state):
        """
        Render the complete game state

        Args:
            game_state: GameState object containing all game data
        """
        self.screen.fill(BG_COLOR)

        # Draw Player 1's view
        self.screen.set_clip(self.clip_p1)
        self._draw_finish_line(game_state.camera_y_p1, self.clip_p1)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p1, self.clip_p1)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane1, game_state.camera_y_p1, self.clip_p1
        )
        self._draw_snake(game_state.snake1, game_state.camera_y_p1, self.clip_p1)

        # Draw Player 2's view
        self.screen.set_clip(self.clip_p2)
        self._draw_finish_line(game_state.camera_y_p2, self.clip_p2)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p2, self.clip_p2)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane2, game_state.camera_y_p2, self.clip_p2
        )
        self._draw_snake(game_state.snake2, game_state.camera_y_p2, self.clip_p2)

        # Draw divider and HUD without clipping
        self.screen.set_clip(None)
        pygame.draw.rect(
            self.screen, DIVIDER_COLOR, pygame.Rect(PANE_COLS * CELL - 2, 0, 4, HEIGHT)
        )
        self._draw_hud(game_state.snake1, game_state.snake2, game_state.winner_text)

        pygame.display.flip()

    def _draw_snake(self, snake, camera_y, clip_rect):
        """Draw a snake"""
        for i, (x, y) in enumerate(snake.body):
            screen_y = y - camera_y
            if -1 <= screen_y <= GRID_H:
                col = snake.head_col if i == 0 else snake.body_col

                # Add glow effect if invincible
                if snake.is_invincible() and i == 0:
                    glow_rect = pygame.Rect(
                        x * CELL - 2, screen_y * CELL - 2, CELL + 4, CELL + 4
                    )
                    if clip_rect is None or glow_rect.colliderect(clip_rect):
                        pygame.draw.rect(
                            self.screen, (255, 255, 200), glow_rect, border_radius=6
                        )

                r = pygame.Rect(
                    x * CELL + PADDING,
                    screen_y * CELL + PADDING,
                    CELL - 2 * PADDING,
                    CELL - 2 * PADDING,
                )
                if clip_rect is None or r.colliderect(clip_rect):
                    pygame.draw.rect(self.screen, col, r, border_radius=4)

    def _draw_apples_for_pane(self, apples, pane, camera_y, clip_rect):
        """Draw apples that belong to a specific pane"""
        for apple in apples:
            if pane.inside(apple.x):
                self._draw_apple(apple, camera_y, clip_rect)

    def _draw_apple(self, apple, camera_y, clip_rect):
        """Draw an apple"""
        screen_y = apple.y - camera_y
        if -1 <= screen_y <= GRID_H:
            color = GOLDEN_APPLE_COLOR if apple.is_golden else RED_APPLE_COLOR
            center_x = apple.x * CELL + CELL // 2
            center_y = int(screen_y * CELL + CELL // 2)

            if clip_rect is None or clip_rect.collidepoint(center_x, center_y):
                radius = int((CELL // 2 - 3) * 1.5)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                # Add shine effect
                shine_offset = radius // 3
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x - shine_offset, center_y - shine_offset),
                    radius // 3,
                )

    def _draw_obstacles(self, obstacles, camera_y, clip_rect):
        """Draw obstacles"""
        for x, y in obstacles.blocks:
            screen_y = y - camera_y
            if -1 <= screen_y <= GRID_H:
                size = int((CELL - 4) * 1.15)
                offset = (CELL - size) // 2
                r = pygame.Rect(x * CELL + offset, screen_y * CELL + offset, size, size)
                if clip_rect is None or r.colliderect(clip_rect):
                    pygame.draw.rect(self.screen, OBSTACLE_A, r, border_radius=4)
                    pygame.draw.rect(
                        self.screen, OBSTACLE_B, r.inflate(-6, -6), border_radius=3
                    )

    def _draw_finish_line(self, camera_y, clip_rect):
        """Draw the finish line"""
        from config import FINISH_LINE_DISTANCE

        screen_y = FINISH_LINE_DISTANCE - camera_y
        if -5 <= screen_y <= GRID_H + 5:
            y_pixel = int(screen_y * CELL)
            # Draw checkered pattern
            for x in range(0, WIDTH, CELL):
                r = pygame.Rect(x, y_pixel, CELL, CELL // 2)
                if clip_rect is None or r.colliderect(clip_rect):
                    color = (
                        FINISH_LINE_COLOR if (x // CELL) % 2 == 0 else (200, 200, 50)
                    )
                    pygame.draw.rect(self.screen, color, r)

    def _draw_hud(self, snake1, snake2, winner_text):
        """Draw the heads-up display"""
        # Player 1 info
        p1_text = f"{snake1.name}: {snake1.apples_collected} apples"
        if snake1.active_powerup == PowerUpType.SPEED_BOOST:
            p1_text += " [SPEED]"
        elif snake1.active_powerup == PowerUpType.INVINCIBILITY:
            p1_text += " [INVINCIBLE]"
        img1 = self.font.render(p1_text, True, P1_HEAD)
        self.screen.blit(img1, (12, 10))

        # Player 2 info
        p2_text = f"{snake2.name}: {snake2.apples_collected} apples"
        if snake2.active_powerup == PowerUpType.SPEED_BOOST:
            p2_text += " [SPEED]"
        elif snake2.active_powerup == PowerUpType.INVINCIBILITY:
            p2_text += " [INVINCIBLE]"
        img2 = self.font.render(p2_text, True, P2_HEAD)
        self.screen.blit(img2, (WIDTH - img2.get_width() - 12, 10))

        # Controls
        controls = self.font.render(
            "P1: A/D   P2: ◀/▶   R: restart   ESC: quit", True, TEXT_COLOR
        )
        self.screen.blit(controls, (12, HEIGHT - 30))

        # Winner text
        if winner_text:
            banner = self.font.render(winner_text, True, TEXT_COLOR)
            rect = banner.get_rect(center=(WIDTH // 2, 32))
            pygame.draw.rect(self.screen, (0, 0, 0, 128), rect.inflate(20, 10))
            self.screen.blit(banner, rect)
