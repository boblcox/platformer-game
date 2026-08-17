"""Combat resolution for units."""

from __future__ import annotations

import random

from .hex_grid import TerrainType
from .units import Unit


class CombatSystem:
    TERRAIN_DEFENSE = {
        TerrainType.FOREST: 0.20,
        TerrainType.MOUNTAIN: 0.30,
    }
    CASTLE_DEFENSE = 0.40

    def calculate_damage(self, attacker: Unit, defender: Unit, terrain_defense_bonus: float) -> int:
        base_damage = attacker.attack - defender.defense * 0.5
        reduced_damage = base_damage * max(0.0, 1.0 - terrain_defense_bonus)
        varied_damage = reduced_damage * random.uniform(0.8, 1.2)
        return max(1, int(round(varied_damage)))

    def can_attack(self, attacker: Unit, target: Unit) -> bool:
        return (
            attacker.owner != target.owner
            and attacker.is_alive()
            and target.is_alive()
            and not attacker.has_attacked
            and attacker.hex_pos.distance(target.hex_pos) <= attacker.attack_range
        )

    def resolve_attack(self, attacker: Unit, defender: Unit, grid) -> dict[str, int | bool]:
        if not self.can_attack(attacker, defender):
            return {"damage": 0, "defender_died": False}

        terrain = grid.get_tile(defender.hex_pos)
        terrain_bonus = self.TERRAIN_DEFENSE.get(terrain, 0.0)
        terrain_bonus = max(terrain_bonus, grid.get_structure_bonus(defender.hex_pos))
        damage = self.calculate_damage(attacker, defender, terrain_bonus)
        defender.take_damage(damage)
        attacker.has_attacked = True
        return {"damage": damage, "defender_died": not defender.is_alive()}
