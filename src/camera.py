"""Camera that follows the player and clamps to map bounds."""

import pygame
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    """Translates world coordinates to screen coordinates."""

    def __init__(self, map_pixel_width: int, map_pixel_height: int) -> None:
        self.offset_x = 0
        self.offset_y = 0
        self.map_w = map_pixel_width
        self.map_h = map_pixel_height

    def update(self, target_rect: pygame.Rect) -> None:
        """Centre the camera on *target_rect*, clamping to map bounds."""
        self.offset_x = target_rect.centerx - SCREEN_WIDTH // 2
        self.offset_y = target_rect.centery - SCREEN_HEIGHT // 2
        self.offset_x = max(0, min(self.offset_x, self.map_w - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.map_h - SCREEN_HEIGHT))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Return a new rect shifted to screen space."""
        return pygame.Rect(
            rect.x - self.offset_x,
            rect.y - self.offset_y,
            rect.width,
            rect.height,
        )

    def apply_pos(self, x: float, y: float) -> tuple:
        """Return a (screen_x, screen_y) tuple for a world position."""
        return x - self.offset_x, y - self.offset_y
