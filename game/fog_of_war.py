"""Fog of war visibility tracking."""

from __future__ import annotations

from dataclasses import dataclass, field

from .hex_grid import HexCoord


@dataclass
class FogOfWar:
    player_id: int
    visible_hexes: set[HexCoord] = field(default_factory=set)
    explored_hexes: set[HexCoord] = field(default_factory=set)

    def update(self, units, buildings, grid) -> None:
        self.visible_hexes.clear()
        for unit in units:
            if unit.owner != self.player_id or not unit.is_alive():
                continue
            for coord in unit.hex_pos.within(unit.vision_range):
                if grid.in_bounds(coord):
                    self.visible_hexes.add(coord)
        for building in buildings:
            if building.owner != self.player_id:
                continue
            for coord in building.hex_pos.within(building.vision_range):
                if grid.in_bounds(coord):
                    self.visible_hexes.add(coord)
        self.explored_hexes |= self.visible_hexes

    def is_visible(self, coord: HexCoord) -> bool:
        return coord in self.visible_hexes

    def is_explored(self, coord: HexCoord) -> bool:
        return coord in self.explored_hexes
