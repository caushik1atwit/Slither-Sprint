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
        self.title_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.menu_font = pygame.font.SysFont("consolas", 24)

        # Create clip rectangles for split screen
        self.clip_p1 = pygame.Rect(0, 0, PANE_COLS * CELL, HEIGHT)
        self.clip_p2 = pygame.Rect(PANE_COLS * CELL, 0, PANE_COLS * CELL, HEIGHT)

    def _apply_invincibility_color(self, base_color, snake):
        """Apply golden invincibility tint to a color"""
        if not snake.is_invincible():
            return base_color

        # Golden tint
        golden = (255, 215, 0)
        boom_intensity = snake.get_boom_intensity()

        # During boom, blend heavily toward gold
        if boom_intensity > 0:
            blend = 0.7 * boom_intensity
        else:
            # Subtle golden tint when invincible but not booming
            blend = 0.3

        r = int(base_color[0] * (1 - blend) + golden[0] * blend)
        g = int(base_color[1] * (1 - blend) + golden[1] * blend)
        b = int(base_color[2] * (1 - blend) + golden[2] * blend)

        return (min(255, r), min(255, g), min(255, b))

    def render(self, game_state):
        """
        Render the complete game state

        Args:
            game_state: GameState object containing all game data
        """
        self.screen.fill(BG_COLOR)

        # Draw Player 1's view
        self.screen.set_clip(self.clip_p1)
        # Draw background color for invincibility
        if game_state.snake1.is_invincible():
            self._draw_invincibility_background(self.clip_p1)

        self._draw_finish_line(game_state.camera_y_p1, self.clip_p1, game_state.snake1)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p1, self.clip_p1, game_state.snake1)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane1, game_state.camera_y_p1, self.clip_p1, game_state.snake1
        )
        self._draw_snake(game_state.snake1, game_state.camera_y_p1, self.clip_p1)

        # Add boom flash overlays for Player 1
        invincibility_boom = game_state.snake1.get_boom_intensity()
        if invincibility_boom > 0:
            self._draw_invincibility_boom_overlay(self.clip_p1, invincibility_boom)

        speed_boost_boom = game_state.snake1.get_speed_boost_boom_intensity()
        if speed_boost_boom > 0:
            self._draw_speed_boost_boom_overlay(self.clip_p1, speed_boost_boom)

        # Draw Player 2's view
        self.screen.set_clip(self.clip_p2)
        # Draw background color for invincibility
        if game_state.snake2.is_invincible():
            self._draw_invincibility_background(self.clip_p2)

        self._draw_finish_line(game_state.camera_y_p2, self.clip_p2, game_state.snake2)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p2, self.clip_p2, game_state.snake2)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane2, game_state.camera_y_p2, self.clip_p2, game_state.snake2
        )
        self._draw_snake(game_state.snake2, game_state.camera_y_p2, self.clip_p2)

        # Add boom flash overlays for Player 2
        invincibility_boom = game_state.snake2.get_boom_intensity()
        if invincibility_boom > 0:
            self._draw_invincibility_boom_overlay(self.clip_p2, invincibility_boom)

        speed_boost_boom = game_state.snake2.get_speed_boost_boom_intensity()
        if speed_boost_boom > 0:
            self._draw_speed_boost_boom_overlay(self.clip_p2, speed_boost_boom)

        # Draw divider and HUD without clipping
        self.screen.set_clip(None)
        pygame.draw.rect(
            self.screen, DIVIDER_COLOR, pygame.Rect(PANE_COLS * CELL - 2, 0, 4, HEIGHT)
        )
        self._draw_hud(game_state.snake1, game_state.snake2, game_state.winner_text,
                       game_state.score_p1, game_state.score_p2)

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

    def _draw_apples_for_pane(self, apples, pane, camera_y, clip_rect, snake):
        """Draw apples that belong to a specific pane"""
        for apple in apples:
            if pane.inside(apple.x):
                self._draw_apple(apple, camera_y, clip_rect, snake)

    def _draw_apple(self, apple, camera_y, clip_rect, snake):
        """Draw an apple"""
        screen_y = apple.y - camera_y
        if -1 <= screen_y <= GRID_H:
            base_color = GOLDEN_APPLE_COLOR if apple.is_golden else RED_APPLE_COLOR
            color = self._apply_invincibility_color(base_color, snake)
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

    def _draw_obstacles(self, obstacles, camera_y, clip_rect, snake):
        """Draw obstacles"""
        for x, y in obstacles.blocks:
            screen_y = y - camera_y
            if -1 <= screen_y <= GRID_H:
                size = int((CELL - 4) * 1.15)
                offset = (CELL - size) // 2
                r = pygame.Rect(x * CELL + offset, screen_y * CELL + offset, size, size)
                if clip_rect is None or r.colliderect(clip_rect):
                    outer_color = self._apply_invincibility_color(OBSTACLE_A, snake)
                    inner_color = self._apply_invincibility_color(OBSTACLE_B, snake)
                    pygame.draw.rect(self.screen, outer_color, r, border_radius=4)
                    pygame.draw.rect(
                        self.screen, inner_color, r.inflate(-6, -6), border_radius=3
                    )

    def _draw_finish_line(self, camera_y, clip_rect, snake):
        """Draw the finish line"""
        from config import FINISH_LINE_DISTANCE

        screen_y = FINISH_LINE_DISTANCE - camera_y
        if -5 <= screen_y <= GRID_H + 5:
            y_pixel = int(screen_y * CELL)
            # Draw checkered pattern
            for x in range(0, WIDTH, CELL):
                r = pygame.Rect(x, y_pixel, CELL, CELL // 2)
                if clip_rect is None or r.colliderect(clip_rect):
                    base_color = (
                        FINISH_LINE_COLOR if (x // CELL) % 2 == 0 else (200, 200, 50)
                    )
                    color = self._apply_invincibility_color(base_color, snake)
                    pygame.draw.rect(self.screen, color, r)

    def _draw_hud(self, snake1, snake2, winner_text, score_p1, score_p2):
        """Draw the heads-up display"""
        # Score at the top center
        score_text = f"P1 vs P2     {score_p1} - {score_p2}"
        score_img = self.menu_font.render(score_text, True, TEXT_COLOR)
        score_rect = score_img.get_rect(center=(WIDTH // 2, 15))
        # Draw background for score
        bg_rect = score_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        self.screen.blit(score_img, score_rect)

        # Player 1 info
        p1_text = f"{snake1.name}: {snake1.apples_collected} apples"
        if snake1.active_powerup == PowerUpType.SPEED_BOOST:
            p1_text += " [SPEED]"
        elif snake1.active_powerup == PowerUpType.INVINCIBILITY:
            p1_text += " [INVINCIBLE]"
        img1 = self.font.render(p1_text, True, P1_HEAD)
        self.screen.blit(img1, (12, 40))

        # Player 2 info
        p2_text = f"{snake2.name}: {snake2.apples_collected} apples"
        if snake2.active_powerup == PowerUpType.SPEED_BOOST:
            p2_text += " [SPEED]"
        elif snake2.active_powerup == PowerUpType.INVINCIBILITY:
            p2_text += " [INVINCIBLE]"
        img2 = self.font.render(p2_text, True, P2_HEAD)
        self.screen.blit(img2, (WIDTH - img2.get_width() - 12, 40))

        # Controls
        controls = self.font.render(
            "P1: A/D   P2: ◀/▶   R: restart   ESC: quit", True, TEXT_COLOR
        )
        self.screen.blit(controls, (12, HEIGHT - 30))

        # Winner text
        if winner_text:
            banner = self.font.render(winner_text, True, TEXT_COLOR)
            rect = banner.get_rect(center=(WIDTH // 2, 65))
            pygame.draw.rect(self.screen, (0, 0, 0, 128), rect.inflate(20, 10))
            self.screen.blit(banner, rect)

    def render_menu(self):
        """Render the landing/menu screen"""
        self.screen.fill(BG_COLOR)

        # Title
        title = self.title_font.render("SLITHER SPRINT", True, (40, 220, 120))
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.menu_font.render("Two-Player Snake Racing", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 60))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        instructions = [
            "",
            "Press SPACE to Start",
            "",
            "Player 1: A / D to steer",
            "Player 2: LEFT / RIGHT arrows to steer",
            "",
            "Collect apples and race to the finish!",
            "Every 3 apples = Speed Boost",
            "Golden apples = Invincibility",
            "",
            "P: Pause   R: Restart   ESC: Quit",
        ]

        y_offset = HEIGHT // 2 + 20
        for line in instructions:
            if line:
                text = self.font.render(line, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
            y_offset += 25

        pygame.display.flip()

    def _draw_invincibility_background(self, clip_rect):
        """Draw a subtle golden background tint for invincibility"""
        # Create a semi-transparent golden background
        background = pygame.Surface((clip_rect.width, clip_rect.height))
        background.set_alpha(25)  # Very subtle tint
        background.fill((255, 215, 0))  # Golden color
        self.screen.blit(background, (clip_rect.x, clip_rect.y))

    def _draw_invincibility_boom_overlay(self, clip_rect, intensity):
        """Draw a golden flash overlay for the invincibility boom effect"""
        # Create a surface with per-pixel alpha
        overlay = pygame.Surface((clip_rect.width, clip_rect.height))
        overlay.set_alpha(int(160 * intensity))  # Max 160 alpha at full intensity
        overlay.fill((255, 215, 0))  # Golden color
        self.screen.blit(overlay, (clip_rect.x, clip_rect.y))

    def _draw_speed_boost_boom_overlay(self, clip_rect, intensity):
        """Draw a red pulsing overlay for the speed boost boom effect"""
        # Create a surface with per-pixel alpha
        overlay = pygame.Surface((clip_rect.width, clip_rect.height))
        overlay.set_alpha(int(120 * intensity))  # Max 120 alpha at full intensity (slightly less intense)
        overlay.fill((255, 50, 50))  # Red color
        self.screen.blit(overlay, (clip_rect.x, clip_rect.y))
