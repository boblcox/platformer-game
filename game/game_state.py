"""Core game state and turn logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .buildings import Building, BuildingType
from .combat import CombatSystem
from .fog_of_war import FogOfWar
from .hex_grid import HexCoord, HexGrid, TerrainType
from .map_gen import MapGenerator
from .pathfinding import AStarPathfinder
from .resources import ResourceManager
from .units import UNIT_STATS, Unit, UnitType


class GamePhase(str, Enum):
    SETUP = "SETUP"
    PLAYING = "PLAYING"
    GAME_OVER = "GAME_OVER"


@dataclass
class Player:
    id: int
    name: str
    color: tuple[int, int, int]
    resources: ResourceManager = field(default_factory=ResourceManager)
    fog: FogOfWar | None = None
    is_ai: bool = False

    def __post_init__(self) -> None:
        if self.fog is None:
            self.fog = FogOfWar(self.id)


@dataclass
class GameState:
    players: list[Player]
    grid: HexGrid
    units: list[Unit]
    buildings: list[Building]
    current_player: int = 0
    turn_number: int = 1
    game_phase: GamePhase = GamePhase.SETUP
    winner: Optional[int] = None
    pathfinder: AStarPathfinder = field(default_factory=AStarPathfinder)
    combat_system: CombatSystem = field(default_factory=CombatSystem)

    @classmethod
    def create_default(cls, width: int = 20, height: int = 15) -> "GameState":
        players = [
            Player(0, "Azure Kingdom", (50, 100, 200), is_ai=False),
            Player(1, "Crimson Dominion", (200, 50, 50), is_ai=True),
        ]
        grid = MapGenerator().generate_map(width, height)
        buildings: list[Building] = [
            Building(BuildingType.CASTLE, 0, grid.starting_positions[0]),
            Building(BuildingType.CASTLE, 1, grid.starting_positions[1]),
        ]
        buildings.extend(Building(BuildingType.VILLAGE, None, coord) for coord in grid.village_positions)
        buildings.extend(Building(BuildingType.BARRACKS, None, coord) for coord in grid.barracks_positions)
        buildings.extend(Building(BuildingType.TOWER, None, coord) for coord in grid.tower_positions)

        units = cls._create_starting_units(grid)
        state = cls(players=players, grid=grid, units=units, buildings=buildings, game_phase=GamePhase.PLAYING)
        state.sync_grid_state()
        state.update_all_fog()
        return state

    @staticmethod
    def _create_starting_units(grid: HexGrid) -> list[Unit]:
        p1 = grid.starting_positions[0]
        p2 = grid.starting_positions[1]
        def spawn_positions(castle: HexCoord) -> list[HexCoord]:
            options = [
                coord
                for coord in castle.within(2)
                if grid.in_bounds(coord)
                and coord != castle
                and grid.get_tile(coord) != TerrainType.WATER
            ]
            options.sort(key=lambda coord: (castle.distance(coord), coord.r, coord.q))
            return options[:3]

        p1_positions = spawn_positions(p1)
        p2_positions = spawn_positions(p2)
        return [
            Unit(UnitType.WARRIOR, 0, p1_positions[0]),
            Unit(UnitType.WARRIOR, 0, p1_positions[1]),
            Unit(UnitType.ARCHER, 0, p1_positions[2]),
            Unit(UnitType.WARRIOR, 1, p2_positions[0]),
            Unit(UnitType.WARRIOR, 1, p2_positions[1]),
            Unit(UnitType.ARCHER, 1, p2_positions[2]),
        ]

    @property
    def active_player(self) -> Player:
        return self.players[self.current_player]

    def sync_grid_state(self) -> None:
        self.grid.clear_structure_bonuses()
        for building in self.buildings:
            if building.building_type == BuildingType.CASTLE:
                self.grid.set_structure_bonus(building.hex_pos, 0.40)
        self.grid.set_occupied(unit.hex_pos for unit in self.units if unit.is_alive())

    def update_all_fog(self) -> None:
        self.sync_grid_state()
        for player in self.players:
            player.fog.update(self.units, self.buildings, self.grid)

    def terrain_movement_cost(self, coord: HexCoord) -> float:
        terrain = self.grid.get_tile(coord)
        if terrain == TerrainType.WATER:
            return float("inf")
        if terrain == TerrainType.MOUNTAIN:
            return 2.0
        if terrain == TerrainType.FOREST:
            return 1.5
        return 1.0

    def get_units_for_player(self, player_id: int) -> list[Unit]:
        return [unit for unit in self.units if unit.owner == player_id and unit.is_alive()]

    def get_buildings_for_player(self, player_id: int) -> list[Building]:
        return [building for building in self.buildings if building.owner == player_id]

    def get_unit_at(self, coord: HexCoord) -> Optional[Unit]:
        for unit in self.units:
            if unit.is_alive() and unit.hex_pos == coord:
                return unit
        return None

    def get_building_at(self, coord: HexCoord) -> Optional[Building]:
        for building in self.buildings:
            if building.hex_pos == coord:
                return building
        return None

    def is_passable(self, coord: HexCoord, moving_unit: Optional[Unit] = None) -> bool:
        if not self.grid.in_bounds(coord):
            return False
        if self.grid.get_tile(coord) == TerrainType.WATER:
            return False
        occupant = self.get_unit_at(coord)
        return occupant is None or occupant == moving_unit

    def calculate_path_cost(self, path: list[HexCoord]) -> float:
        if len(path) <= 1:
            return 0.0
        return sum(self.terrain_movement_cost(step) for step in path[1:])

    def get_recruit_cost(self, building: Building, unit_type: UnitType) -> int:
        base_cost = UNIT_STATS[unit_type]["cost"]
        return max(10, int(base_cost - building.recruitment_bonus))

    def available_recruit_hexes(self, building: Building) -> list[HexCoord]:
        options = []
        for neighbor in self.grid.get_neighbors(building.hex_pos):
            if self.is_passable(neighbor) and self.grid.get_tile(neighbor) != TerrainType.WATER:
                options.append(neighbor)
        options.sort(key=lambda coord: (coord.r, coord.q))
        return options

    def capture_building(self, unit: Unit) -> None:
        building = self.get_building_at(unit.hex_pos)
        if building and building.owner != unit.owner:
            building.owner = unit.owner
            building.hp = building.max_hp

    def move_unit(self, unit: Unit, destination: HexCoord) -> bool:
        if unit.owner != self.current_player or unit.has_moved or not unit.is_alive():
            return False
        if not self.is_passable(destination, moving_unit=unit):
            return False
        path = self.pathfinder.find_path(unit.hex_pos, destination, self.grid, unit)
        if not path:
            return False
        cost = self.calculate_path_cost(path)
        if cost > unit.movement:
            return False
        unit.move_to(destination)
        self.capture_building(unit)
        self.sync_grid_state()
        self.update_all_fog()
        self.check_victory()
        return True

    def attack_unit(self, attacker: Unit, defender: Unit) -> bool:
        if attacker.owner != self.current_player or defender.owner == attacker.owner:
            return False
        result = self.combat_system.resolve_attack(attacker, defender, self.grid)
        if result["damage"] <= 0:
            return False
        if not defender.is_alive():
            self.units = [unit for unit in self.units if unit.is_alive()]
        self.sync_grid_state()
        self.update_all_fog()
        self.check_victory()
        return True

    def recruit_unit(self, building: Building, unit_type: UnitType) -> Optional[Unit]:
        if building.owner != self.current_player or not building.can_recruit():
            return None
        if unit_type not in building.get_recruitable_units():
            return None
        spawn_options = self.available_recruit_hexes(building)
        if not spawn_options:
            return None
        player = self.players[self.current_player]
        cost = self.get_recruit_cost(building, unit_type)
        if not player.resources.spend(cost):
            return None
        unit = Unit(unit_type, self.current_player, spawn_options[0])
        unit.has_moved = True
        unit.has_attacked = True
        self.units.append(unit)
        self.sync_grid_state()
        self.update_all_fog()
        return unit

    def next_turn(self) -> None:
        self.check_victory()
        if self.game_phase == GamePhase.GAME_OVER:
            return
        self.current_player = (self.current_player + 1) % len(self.players)
        if self.current_player == 0:
            self.turn_number += 1
        player = self.active_player
        player.resources.collect_income(self.get_buildings_for_player(player.id))
        player.resources.pay_upkeep(self.get_units_for_player(player.id))
        for unit in self.get_units_for_player(player.id):
            unit.reset_turn()
        self.update_all_fog()
        self.check_victory()

    def is_game_over(self) -> bool:
        for player in self.players:
            units_alive = any(unit.owner == player.id and unit.is_alive() for unit in self.units)
            castles_alive = any(
                building.owner == player.id and building.building_type == BuildingType.CASTLE
                for building in self.buildings
            )
            if not units_alive and not castles_alive:
                return True
        return False

    def check_victory(self) -> Optional[int]:
        defeated_players: list[int] = []
        for player in self.players:
            has_units = any(unit.owner == player.id and unit.is_alive() for unit in self.units)
            has_castle = any(
                building.owner == player.id and building.building_type == BuildingType.CASTLE
                for building in self.buildings
            )
            if not has_units and not has_castle:
                defeated_players.append(player.id)
        if defeated_players:
            surviving = [player.id for player in self.players if player.id not in defeated_players]
            if surviving:
                self.winner = surviving[0]
                self.game_phase = GamePhase.GAME_OVER
        return self.winner

    def get_center_hex(self) -> HexCoord:
        return HexCoord(self.grid.width // 2, self.grid.height // 2)
