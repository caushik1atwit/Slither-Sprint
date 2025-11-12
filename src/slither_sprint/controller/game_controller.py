"""
Game Controller - manages game loop and logic
"""

import pygame
import random
from model.game_state import GameState
from view.renderer import Renderer
from config import (
    WIDTH,
    HEIGHT,
    FPS,
    GRID_H,
    OBSTACLE_SPAWN_EVERY_STEPS,
    OBSTACLE_SPAWN_CHANCE,
    SPAWN_AHEAD_MIN,
    SPAWN_AHEAD_MAX,
    FINISH_LINE_DISTANCE,
)


class GameController:
    """Controls game flow and updates"""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Slither Sprint")
        self.clock = pygame.time.Clock()

        self.game_state = GameState()
        self.renderer = Renderer(self.screen)

        self.acc_ms_p1 = 0
        self.acc_ms_p2 = 0

    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS)

            # Handle events
            if not self._handle_events():
                running = False
                continue

            # Update game
            if self.game_state.winner_text is None:
                self._update_game(dt)

            # Render
            self.renderer.render(self.game_state)

    def _handle_events(self):
        """
        Handle pygame events

        Returns:
            False if should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r:
                    self.game_state.reset()
                    self.acc_ms_p1 = 0
                    self.acc_ms_p2 = 0

        # Handle continuous key presses for steering
        keys = pygame.key.get_pressed()
        self.game_state.snake1.steer(keys[pygame.K_a], keys[pygame.K_d])
        self.game_state.snake2.steer(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        return True

    def _update_game(self, dt):
        """Update game state"""
        # Update power-ups
        self.game_state.snake1.update_powerups()
        self.game_state.snake2.update_powerups()

        # Update snakes with independent timers (for speed boost)
        self._update_snake_movement(dt)

        # Game logic
        self._check_collisions()
        self._handle_apple_collection()
        self._spawn_apples()
        self._update_cameras()
        self._spawn_obstacles()
        self._check_win_conditions()
        self.game_state.cleanup_offscreen_items()

    def _update_snake_movement(self, dt):
        """Update snake positions based on their individual step timers"""
        self.acc_ms_p1 += dt
        self.acc_ms_p2 += dt

        while self.acc_ms_p1 >= self.game_state.snake1.current_step_ms:
            self.acc_ms_p1 -= self.game_state.snake1.current_step_ms
            self.game_state.snake1.step()

        while self.acc_ms_p2 >= self.game_state.snake2.current_step_ms:
            self.acc_ms_p2 -= self.game_state.snake2.current_step_ms
            self.game_state.snake2.step()

    def _check_collisions(self):
        """Check for obstacle collisions"""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2
        obs = self.game_state.obstacles

        if s1.alive and not s1.is_invincible():
            if obs.collides(s1.head):
                s1.alive = False

        if s2.alive and not s2.is_invincible():
            if obs.collides(s2.head):
                s2.alive = False

    def _handle_apple_collection(self):
        """Handle apple collection by snakes"""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2
        apples_to_remove = []

        for apple in self.game_state.apples:
            if s1.alive and s1.head == apple.position:
                if apple.is_golden:
                    s1.collect_golden_apple()
                else:
                    s1.collect_apple()
                apples_to_remove.append(apple)
            elif s2.alive and s2.head == apple.position:
                if apple.is_golden:
                    s2.collect_golden_apple()
                else:
                    s2.collect_apple()
                apples_to_remove.append(apple)

        for apple in apples_to_remove:
            self.game_state.apples.remove(apple)

    def _spawn_apples(self):
        """Spawn new apples randomly"""
        if random.random() < 0.08 and len(self.game_state.apples) < 50:
            self.game_state.spawn_apple()

    def _update_cameras(self):
        """Update camera positions to follow snakes"""
        # Player 1 camera
        target_camera_p1 = self.game_state.snake1.head[1] - GRID_H * 0.75
        self.game_state.camera_y_p1 += (
            target_camera_p1 - self.game_state.camera_y_p1
        ) * 0.2

        # Player 2 camera
        target_camera_p2 = self.game_state.snake2.head[1] - GRID_H * 0.75
        self.game_state.camera_y_p2 += (
            target_camera_p2 - self.game_state.camera_y_p2
        ) * 0.2

    def _spawn_obstacles(self):
        """Spawn obstacles ahead of snakes"""
        self._spawn_obstacles_for_snake(self.game_state.snake1)
        self._spawn_obstacles_for_snake(self.game_state.snake2)

    def _spawn_obstacles_for_snake(self, snake):
        """Spawn obstacles for a specific snake"""
        if not snake.alive:
            return

        if (
            snake.steps % OBSTACLE_SPAWN_EVERY_STEPS == 0
            and random.random() < OBSTACLE_SPAWN_CHANCE
        ):
            ahead = random.randint(SPAWN_AHEAD_MIN, SPAWN_AHEAD_MAX)
            hx, hy = snake.head
            y = hy - ahead
            span = random.choice([1, 2, 3])
            start_x = random.randint(snake.pane.x0, snake.pane.x1 - (span - 1))

            for i in range(span):
                self.game_state.obstacles.add(start_x + i, y)

    def _check_win_conditions(self):
        """Check if game has ended"""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2

        # Check for finish line
        if s1.alive and s1.head[1] <= FINISH_LINE_DISTANCE:
            self.game_state.winner_text = f"{s1.name} wins! Reached the finish line!"
        elif s2.alive and s2.head[1] <= FINISH_LINE_DISTANCE:
            self.game_state.winner_text = f"{s2.name} wins! Reached the finish line!"
        # Check for crashes
        elif not s1.alive and s2.alive:
            self.game_state.winner_text = f"{s2.name} wins! {s1.name} crashed!"
        elif not s2.alive and s1.alive:
            self.game_state.winner_text = f"{s1.name} wins! {s2.name} crashed!"
        elif not s1.alive and not s2.alive:
            self.game_state.winner_text = "Draw! Both crashed!"
