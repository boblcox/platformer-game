"""Hex grid coordinate math and tile storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, Iterable, Iterator, Optional


class TerrainType(str, Enum):
    GRASS = "GRASS"
    FOREST = "FOREST"
    MOUNTAIN = "MOUNTAIN"
    WATER = "WATER"
    DESERT = "DESERT"


@dataclass(frozen=True, order=True)
class HexCoord:
    q: int
    r: int
    s: int | None = None

    def __post_init__(self) -> None:
        computed_s = -self.q - self.r if self.s is None else self.s
        object.__setattr__(self, "s", computed_s)
        if self.q + self.r + computed_s != 0:
            raise ValueError("Cube coordinates must satisfy q + r + s == 0")

    @staticmethod
    def directions() -> tuple["HexCoord", ...]:
        return (
            HexCoord(1, 0, -1),
            HexCoord(1, -1, 0),
            HexCoord(0, -1, 1),
            HexCoord(-1, 0, 1),
            HexCoord(-1, 1, 0),
            HexCoord(0, 1, -1),
        )

    def __add__(self, other: "HexCoord") -> "HexCoord":
        return HexCoord(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other: "HexCoord") -> "HexCoord":
        return HexCoord(self.q - other.q, self.r - other.r, self.s - other.s)

    def neighbors(self) -> list["HexCoord"]:
        return [self + direction for direction in self.directions()]

    def distance(self, other: "HexCoord") -> int:
        return max(abs(self.q - other.q), abs(self.r - other.r), abs(self.s - other.s))

    def ring(self, radius: int) -> list["HexCoord"]:
        if radius < 0:
            return []
        if radius == 0:
            return [self]
        results: list[HexCoord] = []
        cube = self + HexCoord.directions()[4] * radius
        for direction in HexCoord.directions():
            for _ in range(radius):
                results.append(cube)
                cube = cube + direction
        return results

    def within(self, radius: int) -> list["HexCoord"]:
        coords: list[HexCoord] = []
        for dq in range(-radius, radius + 1):
            for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                ds = -dq - dr
                coords.append(HexCoord(self.q + dq, self.r + dr, self.s + ds))
        return coords

    def to_pixel(self, hex_size: float = 40.0) -> tuple[float, float]:
        x = hex_size * (1.5 * self.q)
        y = hex_size * (math.sqrt(3) * (self.r + self.q / 2))
        return x, y

    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float = 40.0) -> "HexCoord":
        q = (2.0 / 3.0 * x) / hex_size
        r = ((-1.0 / 3.0) * x + (math.sqrt(3) / 3.0) * y) / hex_size
        return cls.cube_round(q, r, -q - r)

    @classmethod
    def cube_round(cls, q: float, r: float, s: float) -> "HexCoord":
        rq = round(q)
        rr = round(r)
        rs = round(s)

        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)

        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        else:
            rs = -rq - rr
        return cls(int(rq), int(rr), int(rs))

    def __mul__(self, value: int) -> "HexCoord":
        return HexCoord(self.q * value, self.r * value, self.s * value)


@dataclass
class HexGrid:
    width: int = 20
    height: int = 15
    hex_size: float = 40.0
    tiles: Dict[HexCoord, TerrainType] = field(default_factory=dict)
    starting_positions: dict[int, HexCoord] = field(default_factory=dict)
    village_positions: list[HexCoord] = field(default_factory=list)
    barracks_positions: list[HexCoord] = field(default_factory=list)
    tower_positions: list[HexCoord] = field(default_factory=list)
    structure_bonuses: dict[HexCoord, float] = field(default_factory=dict)
    occupied_hexes: set[HexCoord] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.tiles:
            for q in range(self.width):
                for r in range(self.height):
                    self.tiles[HexCoord(q, r)] = TerrainType.GRASS

    def all_hexes(self) -> list[HexCoord]:
        return list(self.tiles.keys())

    def __iter__(self) -> Iterator[HexCoord]:
        return iter(self.tiles)

    def in_bounds(self, coord: HexCoord) -> bool:
        return 0 <= coord.q < self.width and 0 <= coord.r < self.height

    def get_tile(self, coord: HexCoord) -> Optional[TerrainType]:
        return self.tiles.get(coord)

    def set_tile(self, coord: HexCoord, terrain: TerrainType) -> None:
        if self.in_bounds(coord):
            self.tiles[coord] = terrain

    def get_neighbors(self, coord: HexCoord, passable_only: bool = False) -> list[HexCoord]:
        neighbors = [neighbor for neighbor in coord.neighbors() if self.in_bounds(neighbor)]
        if not passable_only:
            return neighbors
        return [neighbor for neighbor in neighbors if self.get_tile(neighbor) != TerrainType.WATER]

    def axial_to_pixel(self, coord: HexCoord) -> tuple[float, float]:
        return coord.to_pixel(self.hex_size)

    def pixel_to_axial(self, x: float, y: float) -> HexCoord:
        return HexCoord.from_pixel(x, y, self.hex_size)

    def hex_corners(self, coord: HexCoord) -> list[tuple[float, float]]:
        center_x, center_y = self.axial_to_pixel(coord)
        points: list[tuple[float, float]] = []
        for index in range(6):
            angle = math.radians(60 * index)
            points.append(
                (
                    center_x + self.hex_size * math.cos(angle),
                    center_y + self.hex_size * math.sin(angle),
                )
            )
        return points

    def set_structure_bonus(self, coord: HexCoord, bonus: float) -> None:
        self.structure_bonuses[coord] = bonus

    def clear_structure_bonuses(self) -> None:
        self.structure_bonuses.clear()

    def get_structure_bonus(self, coord: HexCoord) -> float:
        return self.structure_bonuses.get(coord, 0.0)

    def set_occupied(self, coords: Iterable[HexCoord]) -> None:
        self.occupied_hexes = set(coords)

    def is_occupied(self, coord: HexCoord) -> bool:
        return coord in self.occupied_hexes
