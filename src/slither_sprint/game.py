"""
Slither Sprint - Entry Point
Two-player vertical snake racing game
"""

import pygame
from controller.game_controller import GameController


def main():
    pygame.init()
    controller = GameController()
    controller.run()
    pygame.quit()


if __name__ == "__main__":
    main()
