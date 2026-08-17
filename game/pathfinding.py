"""A* pathfinding on the hex grid."""

from __future__ import annotations

import heapq
from itertools import count

from .hex_grid import HexCoord, TerrainType


class AStarPathfinder:
    MOVEMENT_COSTS = {
        TerrainType.GRASS: 1.0,
        TerrainType.DESERT: 1.0,
        TerrainType.FOREST: 1.5,
        TerrainType.MOUNTAIN: 2.0,
        TerrainType.WATER: float("inf"),
    }

    def heuristic(self, start: HexCoord, end: HexCoord) -> float:
        return float(start.distance(end))

    def terrain_cost(self, terrain: TerrainType) -> float:
        return self.MOVEMENT_COSTS.get(terrain, 1.0)

    def reconstruct_path(self, came_from: dict[HexCoord, HexCoord], current: HexCoord) -> list[HexCoord]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def find_path(self, start: HexCoord, end: HexCoord, grid, unit) -> list[HexCoord]:
        if start == end:
            return [start]
        if not grid.in_bounds(start) or not grid.in_bounds(end):
            return []
        if self.terrain_cost(grid.get_tile(end)) == float("inf"):
            return []

        frontier: list[tuple[float, int, HexCoord]] = []
        sequence = count()
        heapq.heappush(frontier, (0.0, next(sequence), start))
        came_from: dict[HexCoord, HexCoord] = {}
        cost_so_far: dict[HexCoord, float] = {start: 0.0}

        while frontier:
            _, _, current = heapq.heappop(frontier)
            if current == end:
                return self.reconstruct_path(came_from, current)

            for neighbor in grid.get_neighbors(current):
                terrain = grid.get_tile(neighbor)
                move_cost = self.terrain_cost(terrain)
                if move_cost == float("inf"):
                    continue
                if grid.is_occupied(neighbor) and neighbor != end:
                    continue
                new_cost = cost_so_far[current] + move_cost
                if new_cost < cost_so_far.get(neighbor, float("inf")):
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, end)
                    heapq.heappush(frontier, (priority, next(sequence), neighbor))
                    came_from[neighbor] = current
        return []
