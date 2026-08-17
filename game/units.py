"""Unit data and behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import itertools

from .hex_grid import HexCoord


class UnitType(str, Enum):
    WARRIOR = "WARRIOR"
    ARCHER = "ARCHER"
    MAGE = "MAGE"
    CAVALRY = "CAVALRY"
    CATAPULT = "CATAPULT"


UNIT_STATS = {
    UnitType.WARRIOR: dict(hp=100, attack=20, defense=15, movement=3, vision_range=3, attack_range=1, cost=50, upkeep=2),
    UnitType.ARCHER: dict(hp=70, attack=25, defense=8, movement=3, vision_range=4, attack_range=3, cost=60, upkeep=2),
    UnitType.MAGE: dict(hp=60, attack=35, defense=5, movement=2, vision_range=3, attack_range=2, cost=80, upkeep=3),
    UnitType.CAVALRY: dict(hp=90, attack=22, defense=10, movement=5, vision_range=4, attack_range=1, cost=70, upkeep=3),
    UnitType.CATAPULT: dict(hp=80, attack=40, defense=3, movement=2, vision_range=2, attack_range=4, cost=100, upkeep=5),
}

_UNIT_ID = itertools.count(1)


@dataclass
class Unit:
    unit_type: UnitType
    owner: int
    hex_pos: HexCoord
    hp: int = field(init=False)
    max_hp: int = field(init=False)
    attack: int = field(init=False)
    defense: int = field(init=False)
    movement: int = field(init=False)
    vision_range: int = field(init=False)
    attack_range: int = field(init=False)
    cost: int = field(init=False)
    upkeep: int = field(init=False)
    has_moved: bool = False
    has_attacked: bool = False
    unit_id: int = field(default_factory=lambda: next(_UNIT_ID))

    def __post_init__(self) -> None:
        stats = UNIT_STATS[self.unit_type]
        self.max_hp = stats["hp"]
        self.hp = stats["hp"]
        self.attack = stats["attack"]
        self.defense = stats["defense"]
        self.movement = stats["movement"]
        self.vision_range = stats["vision_range"]
        self.attack_range = stats["attack_range"]
        self.cost = stats["cost"]
        self.upkeep = stats["upkeep"]

    @property
    def name(self) -> str:
        return self.unit_type.value.title()

    def can_move_to(self, target_hex: HexCoord) -> bool:
        return not self.has_moved and self.hex_pos != target_hex and self.hex_pos.distance(target_hex) <= self.movement

    def move_to(self, target_hex: HexCoord) -> None:
        self.hex_pos = target_hex
        self.has_moved = True

    def reset_turn(self) -> None:
        self.has_moved = False
        self.has_attacked = False

    def in_attack_range(self, target_hex: HexCoord) -> bool:
        return self.hex_pos.distance(target_hex) <= self.attack_range

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def is_alive(self) -> bool:
        return self.hp > 0
