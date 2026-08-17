"""Per-player resource management."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResourceManager:
    gold: int = 100

    def collect_income(self, buildings) -> int:
        income = sum(building.generate_income() for building in buildings)
        self.gold += income
        return income

    def pay_upkeep(self, units) -> int:
        upkeep = sum(unit.upkeep for unit in units if unit.is_alive())
        self.gold -= upkeep
        return upkeep

    def can_afford(self, cost: int) -> bool:
        return self.gold >= cost

    def spend(self, cost: int) -> bool:
        if not self.can_afford(cost):
            return False
        self.gold -= cost
        return True

    def earn(self, amount: int) -> None:
        self.gold += amount
