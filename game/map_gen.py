"""Procedural map generation for the strategy game."""

from __future__ import annotations

from dataclasses import dataclass
import random

import numpy as np

from .hex_grid import HexCoord, HexGrid, TerrainType


@dataclass
class MapGenerator:
    seed: int | None = None

    def generate_map(self, width: int, height: int) -> HexGrid:
        rng = np.random.default_rng(self.seed)
        grid = HexGrid(width=width, height=height)
        terrain_choices = [
            TerrainType.GRASS,
            TerrainType.FOREST,
            TerrainType.MOUNTAIN,
            TerrainType.WATER,
            TerrainType.DESERT,
        ]
        terrain_probs = np.array([0.60, 0.15, 0.10, 0.10, 0.05], dtype=float)
        roll = rng.random((width, height))
        cumulative = np.cumsum(terrain_probs)

        for q in range(width):
            for r in range(height):
                value = roll[q, r]
                terrain = terrain_choices[0]
                for index, threshold in enumerate(cumulative):
                    if value <= threshold:
                        terrain = terrain_choices[index]
                        break
                grid.set_tile(HexCoord(q, r), terrain)

        start_p1 = HexCoord(1, 1)
        start_p2 = HexCoord(width - 2, height - 2)
        grid.starting_positions = {0: start_p1, 1: start_p2}
        grid.set_tile(start_p1, TerrainType.GRASS)
        grid.set_tile(start_p2, TerrainType.GRASS)

        village_count = random.Random(self.seed).randint(3, 4)
        candidates = [
            HexCoord(q, r)
            for q in range(width)
            for r in range(height)
            if HexCoord(q, r) not in {start_p1, start_p2}
            and grid.get_tile(HexCoord(q, r)) != TerrainType.WATER
        ]
        rng.shuffle(candidates)
        grid.village_positions = sorted(candidates[:village_count])

        special_candidates = [coord for coord in candidates[village_count:] if coord.q not in {0, width - 1} and coord.r not in {0, height - 1}]
        if special_candidates:
            center = HexCoord(width // 2, height // 2)
            tower_pos = min(special_candidates, key=lambda coord: coord.distance(center))
            grid.tower_positions = [tower_pos]
            special_candidates = [coord for coord in special_candidates if coord != tower_pos]
        else:
            grid.tower_positions = []

        barracks_targets = [HexCoord(width // 3, height // 2), HexCoord((2 * width) // 3, height // 2)]
        grid.barracks_positions = []
        for target in barracks_targets:
            if not special_candidates:
                break
            best = min(special_candidates, key=lambda coord: coord.distance(target))
            grid.barracks_positions.append(best)
            special_candidates = [coord for coord in special_candidates if coord != best]

        for coord in grid.village_positions + grid.barracks_positions + grid.tower_positions:
            if grid.get_tile(coord) == TerrainType.WATER:
                grid.set_tile(coord, TerrainType.GRASS)
        return grid
