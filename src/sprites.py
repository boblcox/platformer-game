"""Non-player / non-enemy game sprites.

Includes:
  * WeaponPickup  – collectible weapon on the floor
  * Projectile    – fired by player (ranged / magic weapons)
  * Ladder        – exit trigger at the end of each level
"""

from __future__ import annotations

import math
from typing import List

import pygame

from src.settings import (
    TILE_SIZE,
    TILE_EMPTY,
    TILE_GROUND,
    TILE_PLATFORM,
    TILE_WALL,
    WEAPONS,
    GOLD,
    YELLOW,
    GREEN,
    DARK_GREEN,
    WHITE,
    BLACK,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_solid_tiles(tiles: list, rect: pygame.Rect) -> List[pygame.Rect]:
    """Return a list of solid tile rects that overlap *rect*."""
    h = len(tiles)
    w = len(tiles[0]) if h else 0
    left_col = max(0, rect.left // TILE_SIZE)
    right_col = min(w - 1, rect.right // TILE_SIZE)
    top_row = max(0, rect.top // TILE_SIZE)
    bot_row = min(h - 1, rect.bottom // TILE_SIZE)
    solid = []
    for row in range(top_row, bot_row + 1):
        for col in range(left_col, right_col + 1):
            if tiles[row][col] in (TILE_GROUND, TILE_PLATFORM, TILE_WALL):
                solid.append(
                    pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                )
    return solid


# ---------------------------------------------------------------------------
# WeaponPickup
# ---------------------------------------------------------------------------

class WeaponPickup(pygame.sprite.Sprite):
    """A weapon lying on the ground waiting to be collected."""

    SIZE = 20
    BOB_SPEED = 0.05
    BOB_AMP = 4

    def __init__(self, x: int, y: int, weapon_key: str) -> None:
        super().__init__()
        self.weapon_key = weapon_key
        self.info = WEAPONS[weapon_key]
        self.base_y = float(y)
        self.bob_offset = 0.0
        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self._draw_icon()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _draw_icon(self) -> None:
        self.image.fill((0, 0, 0, 0))
        color = self.info["color"]
        pygame.draw.rect(self.image, color, (2, 2, self.SIZE - 4, self.SIZE - 4), border_radius=3)
        pygame.draw.rect(self.image, WHITE, (2, 2, self.SIZE - 4, self.SIZE - 4), 1, border_radius=3)

    def update(self) -> None:  # type: ignore[override]
        self.bob_offset += self.BOB_SPEED
        self.rect.y = int(self.base_y + math.sin(self.bob_offset) * self.BOB_AMP)

    def draw(self, surface: pygame.Surface, camera) -> None:
        screen_rect = camera.apply(self.rect)
        surface.blit(self.image, screen_rect)
        # Label
        try:
            font = pygame.font.SysFont("Arial", 10)
        except Exception:
            font = pygame.font.Font(None, 12)
        label = font.render(self.info["name"], True, GOLD)
        lx = screen_rect.centerx - label.get_width() // 2
        ly = screen_rect.top - 14
        surface.blit(label, (lx, ly))


# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------

class Projectile(pygame.sprite.Sprite):
    """A moving projectile fired by the player."""

    LIFETIME = 180  # frames

    def __init__(
        self,
        x: float,
        y: float,
        vel_x: float,
        vel_y: float,
        damage: int,
        size: int,
        color: tuple,
        owner: str = "player",
    ) -> None:
        super().__init__()
        self.fx = float(x)
        self.fy = float(y)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.damage = damage
        self.owner = owner   # "player" or "enemy"
        self.life = self.LIFETIME
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, WHITE, (size // 2, size // 2), size // 2, 1)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, tiles: list) -> None:  # type: ignore[override]
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return

        self.fx += self.vel_x
        self.fy += self.vel_y
        self.rect.center = (int(self.fx), int(self.fy))

        # Kill on solid-tile collision
        for tr in _get_solid_tiles(tiles, self.rect):
            if self.rect.colliderect(tr):
                self.kill()
                return

    def draw(self, surface: pygame.Surface, camera) -> None:
        surface.blit(self.image, camera.apply(self.rect))


# ---------------------------------------------------------------------------
# Ladder  (exit trigger)
# ---------------------------------------------------------------------------

class Ladder:
    """Drawn as a yellow ladder; touching it completes the level."""

    WIDTH = TILE_SIZE
    HEIGHT = TILE_SIZE * 2

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)

    def draw(self, surface: pygame.Surface, camera) -> None:
        sr = camera.apply(self.rect)
        # Rails
        rail_w = 5
        pygame.draw.rect(surface, YELLOW, (sr.left, sr.top, rail_w, sr.height))
        pygame.draw.rect(surface, YELLOW, (sr.right - rail_w, sr.top, rail_w, sr.height))
        # Rungs
        num_rungs = 4
        rung_h = 4
        gap = sr.height // (num_rungs + 1)
        for i in range(1, num_rungs + 1):
            ry = sr.top + i * gap
            pygame.draw.rect(surface, GOLD, (sr.left, ry, sr.width, rung_h))
        # Glow outline
        pygame.draw.rect(surface, GREEN, sr, 2)
