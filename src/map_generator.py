"""Procedural level generator.

Each call to :meth:`MapGenerator.generate` produces a fresh tile grid plus
spawn positions for the player, enemies, weapon pick-ups, and the exit ladder.
"""

from __future__ import annotations

import random
from typing import List, Tuple

import pygame

from src.settings import (
    BASE_MAP_WIDTH,
    MAP_HEIGHT,
    TILE_EMPTY,
    TILE_GROUND,
    TILE_PLATFORM,
    TILE_WALL,
    TILE_SIZE,
    WEAPONS,
)

# Type aliases
Tiles = List[List[int]]
Pos = Tuple[int, int]
WeaponPos = Tuple[int, int, str]


class MapGenerator:
    """Generates one level worth of tiles and entity spawn data."""

    def __init__(self, level: int = 1) -> None:
        self.level = level
        self.seed = random.randint(0, 9_999_999)
        self.width = BASE_MAP_WIDTH + (level - 1) * 5
        self.height = MAP_HEIGHT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
    ) -> Tuple[Tiles, Pos, List[Pos], List[WeaponPos], Pos]:
        """Return (tiles, player_pos, enemy_positions, weapon_positions, ladder_pos)."""
        rng = random.Random(self.seed)
        w, h = self.width, self.height

        tiles = self._blank_map(w, h)
        self._fill_ground(tiles, w, h)
        self._add_pits(tiles, w, h, rng)
        self._add_platforms(tiles, w, h, rng)

        player_pos = self._player_start(h)
        ladder_pos = self._place_ladder(tiles, w, h)
        enemy_positions = self._place_enemies(tiles, w, h, rng)
        weapon_positions = self._place_weapons(tiles, w, h, rng)

        return tiles, player_pos, enemy_positions, weapon_positions, ladder_pos

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _blank_map(w: int, h: int) -> Tiles:
        return [[TILE_EMPTY] * w for _ in range(h)]

    @staticmethod
    def _fill_ground(tiles: Tiles, w: int, h: int) -> None:
        """Solid ground at the two bottom rows plus thin side-walls."""
        for col in range(w):
            tiles[h - 1][col] = TILE_GROUND
            tiles[h - 2][col] = TILE_GROUND
        for row in range(h):
            tiles[row][0] = TILE_WALL
            tiles[row][w - 1] = TILE_WALL

    @staticmethod
    def _add_pits(tiles: Tiles, w: int, h: int, rng: random.Random) -> None:
        """Add a few gaps in the floor starting from level 2."""
        level = rng.randint(1, 10)  # rough proxy – actual level tracked externally
        num_pits = rng.randint(0, 3)
        for _ in range(num_pits):
            pit_col = rng.randint(12, w - 15)
            pit_width = rng.randint(2, 3)
            for dc in range(pit_width):
                c = pit_col + dc
                if 1 < c < w - 5:
                    tiles[h - 1][c] = TILE_EMPTY
                    tiles[h - 2][c] = TILE_EMPTY

    def _add_platforms(self, tiles: Tiles, w: int, h: int, rng: random.Random) -> None:
        """Generate floating platforms at four height bands.

        Platform rows relative to map bottom (h-indexed):
          band 0 → h-5   (low)
          band 1 → h-8   (mid-low)
          band 2 → h-11  (mid-high)
          band 3 → h-14  (high)
        Each row is reachable by a running jump from the band below.
        """
        platform_rows = [h - 5, h - 8, h - 11, h - 14]
        platform_rows = [r for r in platform_rows if r >= 2]

        for row in platform_rows:
            col = rng.randint(3, 7)
            while col < w - 4:
                gap = rng.randint(2, 5)
                col += gap
                plat_len = rng.randint(3, 7)
                end = col + plat_len
                if end >= w - 2:
                    break
                for dc in range(plat_len):
                    tiles[row][col + dc] = TILE_PLATFORM
                col = end

    # ------------------------------------------------------------------

    @staticmethod
    def _player_start(h: int) -> Pos:
        """Spawn just above the ground, near the left edge."""
        x = 3 * TILE_SIZE
        y = (h - 3) * TILE_SIZE  # top of ground surface
        return x, y

    @staticmethod
    def _place_ladder(tiles: Tiles, w: int, h: int) -> Pos:
        """Clear a 2-tile column near the right side and return its pixel pos."""
        col = w - 5
        row = h - 4  # two tiles above ground surface
        tiles[row][col] = TILE_EMPTY
        tiles[row - 1][col] = TILE_EMPTY
        return col * TILE_SIZE, row * TILE_SIZE

    def _place_enemies(
        self, tiles: Tiles, w: int, h: int, rng: random.Random
    ) -> List[Pos]:
        """Return pixel positions for enemy spawns."""
        num_enemies = 3 + self.level * 2
        positions: List[Pos] = []

        for _ in range(num_enemies * 4):
            if len(positions) >= num_enemies:
                break
            col = rng.randint(8, w - 6)
            for row in range(1, h - 1):
                if (
                    tiles[row][col] in (TILE_GROUND, TILE_PLATFORM)
                    and tiles[row - 1][col] == TILE_EMPTY
                ):
                    x = col * TILE_SIZE
                    y = (row - 1) * TILE_SIZE
                    if x > 6 * TILE_SIZE:
                        if not any(abs(x - ex) < 80 for ex, _ in positions):
                            positions.append((x, y))
                    break

        return positions

    def _place_weapons(
        self, tiles: Tiles, w: int, h: int, rng: random.Random
    ) -> List[WeaponPos]:
        """Return (x, y, weapon_key) tuples for weapon pickups."""
        pickable = [k for k in WEAPONS if k != "fists"]
        count = min(len(pickable), 2 + self.level)
        chosen = rng.sample(pickable, min(count, len(pickable)))
        positions: List[WeaponPos] = []

        for weapon_key in chosen:
            col = rng.randint(6, w - 6)
            for row in range(1, h - 1):
                if (
                    tiles[row][col] in (TILE_GROUND, TILE_PLATFORM)
                    and tiles[row - 1][col] == TILE_EMPTY
                ):
                    positions.append((col * TILE_SIZE, (row - 1) * TILE_SIZE, weapon_key))
                    break

        return positions
