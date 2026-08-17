"""Camera controls for map navigation."""

from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class Camera:
    offset_x: float = 120.0
    offset_y: float = 120.0
    zoom: float = 1.0
    min_zoom: float = 0.5
    max_zoom: float = 2.0
    pan_speed: float = 12.0

    def pan(self, dx: float, dy: float) -> None:
        self.offset_x += dx
        self.offset_y += dy

    def zoom_in(self, factor: float = 1.1) -> None:
        self.zoom = min(self.max_zoom, self.zoom * factor)

    def zoom_out(self, factor: float = 1.1) -> None:
        self.zoom = max(self.min_zoom, self.zoom / factor)

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        return int(x * self.zoom + self.offset_x), int(y * self.zoom + self.offset_y)

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        return (x - self.offset_x) / self.zoom, (y - self.offset_y) / self.zoom

    def handle_keyboard(self, pressed_keys) -> None:
        dx = dy = 0.0
        if pressed_keys[pygame.K_a] or pressed_keys[pygame.K_LEFT]:
            dx += self.pan_speed
        if pressed_keys[pygame.K_d] or pressed_keys[pygame.K_RIGHT]:
            dx -= self.pan_speed
        if pressed_keys[pygame.K_w] or pressed_keys[pygame.K_UP]:
            dy += self.pan_speed
        if pressed_keys[pygame.K_s] or pressed_keys[pygame.K_DOWN]:
            dy -= self.pan_speed
        if dx or dy:
            self.pan(dx, dy)
