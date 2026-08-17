"""AI player decision making."""

from __future__ import annotations

from dataclasses import dataclass

from .buildings import Building, BuildingType
from .game_state import GameState
from .hex_grid import HexCoord
from .pathfinding import AStarPathfinder
from .units import Unit, UnitType


@dataclass
class Action:
    pass


@dataclass
class MoveAction(Action):
    unit: Unit
    destination: HexCoord


@dataclass
class AttackAction(Action):
    attacker: Unit
    defender: Unit


@dataclass
class RecruitAction(Action):
    building: Building
    unit_type: UnitType


class AIPlayer:
    def __init__(self, player_id: int) -> None:
        self.player_id = player_id
        self.pathfinder = AStarPathfinder()

    def evaluate_board(self, game_state: GameState) -> float:
        own_units = game_state.get_units_for_player(self.player_id)
        enemy_units = [unit for unit in game_state.units if unit.owner != self.player_id and unit.is_alive()]
        own_buildings = game_state.get_buildings_for_player(self.player_id)
        enemy_buildings = [building for building in game_state.buildings if building.owner not in (None, self.player_id)]
        own_strength = sum(unit.hp + unit.attack + unit.defense for unit in own_units) + sum(building.hp for building in own_buildings)
        enemy_strength = sum(unit.hp + unit.attack + unit.defense for unit in enemy_units) + sum(building.hp for building in enemy_buildings)
        gold_delta = game_state.players[self.player_id].resources.gold - game_state.players[1 - self.player_id].resources.gold
        return own_strength - enemy_strength + gold_delta * 0.5

    def _visible_enemies(self, game_state: GameState):
        fog = game_state.players[self.player_id].fog
        return [unit for unit in game_state.units if unit.owner != self.player_id and unit.hex_pos in fog.visible_hexes and unit.is_alive()]

    def _pick_attack(self, unit: Unit, enemies: list[Unit]) -> AttackAction | None:
        in_range = [enemy for enemy in enemies if unit.in_attack_range(enemy.hex_pos)]
        if not in_range or unit.has_attacked:
            return None
        target = min(in_range, key=lambda enemy: (enemy.hp, unit.hex_pos.distance(enemy.hex_pos)))
        return AttackAction(unit, target)

    def _move_toward(self, game_state: GameState, unit: Unit, target_hex: HexCoord) -> MoveAction | None:
        if unit.has_moved:
            return None
        path = self.pathfinder.find_path(unit.hex_pos, target_hex, game_state.grid, unit)
        if len(path) <= 1:
            return None
        cost = 0.0
        destination = unit.hex_pos
        for step in path[1:]:
            step_cost = game_state.terrain_movement_cost(step)
            if cost + step_cost > unit.movement:
                break
            if game_state.get_unit_at(step) is not None and step != unit.hex_pos:
                break
            cost += step_cost
            destination = step
        if destination == unit.hex_pos:
            return None
        return MoveAction(unit, destination)

    def decide_actions(self, game_state: GameState) -> list[Action]:
        actions: list[Action] = []
        own_units = [unit for unit in game_state.get_units_for_player(self.player_id) if unit.is_alive()]
        visible_enemies = self._visible_enemies(game_state)

        for unit in sorted(own_units, key=lambda item: (item.has_attacked, item.hp)):
            attack = self._pick_attack(unit, visible_enemies)
            if attack:
                actions.append(attack)

        center = game_state.get_center_hex()
        for unit in own_units:
            if any(isinstance(action, AttackAction) and action.attacker == unit for action in actions):
                continue
            if visible_enemies:
                target = min(visible_enemies, key=lambda enemy: unit.hex_pos.distance(enemy.hex_pos))
                move = self._move_toward(game_state, unit, target.hex_pos)
            else:
                move = self._move_toward(game_state, unit, center)
            if move:
                actions.append(move)

        player = game_state.players[self.player_id]
        simulated_gold = player.resources.gold
        for building in game_state.get_buildings_for_player(self.player_id):
            if building.building_type not in {BuildingType.CASTLE, BuildingType.BARRACKS}:
                continue
            if not game_state.available_recruit_hexes(building):
                continue
            for unit_type in (UnitType.ARCHER, UnitType.WARRIOR, UnitType.CAVALRY, UnitType.MAGE, UnitType.CATAPULT):
                if unit_type not in building.get_recruitable_units():
                    continue
                cost = game_state.get_recruit_cost(building, unit_type)
                if simulated_gold >= cost:
                    actions.append(RecruitAction(building, unit_type))
                    simulated_gold -= cost
                    break
        return actions

    def execute_actions(self, game_state: GameState) -> list[Action]:
        actions = self.decide_actions(game_state)
        for action in actions:
            if isinstance(action, AttackAction):
                if action.attacker in game_state.units and action.defender in game_state.units:
                    game_state.attack_unit(action.attacker, action.defender)
            elif isinstance(action, MoveAction):
                if action.unit in game_state.units:
                    game_state.move_unit(action.unit, action.destination)
            elif isinstance(action, RecruitAction):
                game_state.recruit_unit(action.building, action.unit_type)
        return actions
