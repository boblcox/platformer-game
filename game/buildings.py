"""Building data and recruitment rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .hex_grid import HexCoord
from .units import UnitType


class BuildingType(str, Enum):
    CASTLE = "CASTLE"
    VILLAGE = "VILLAGE"
    BARRACKS = "BARRACKS"
    TOWER = "TOWER"


BUILDING_STATS = {
    BuildingType.CASTLE: dict(hp=300, gold_income=10, recruitment_bonus=0, vision_range=4),
    BuildingType.VILLAGE: dict(hp=100, gold_income=5, recruitment_bonus=0, vision_range=2),
    BuildingType.BARRACKS: dict(hp=150, gold_income=0, recruitment_bonus=10, vision_range=3),
    BuildingType.TOWER: dict(hp=120, gold_income=0, recruitment_bonus=0, vision_range=6),
}


@dataclass
class Building:
    building_type: BuildingType
    owner: Optional[int]
    hex_pos: HexCoord
    hp: int = field(init=False)
    max_hp: int = field(init=False)
    gold_income: int = field(init=False)
    recruitment_bonus: int = field(init=False)
    vision_range: int = field(init=False)

    def __post_init__(self) -> None:
        stats = BUILDING_STATS[self.building_type]
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.gold_income = stats["gold_income"]
        self.recruitment_bonus = stats["recruitment_bonus"]
        self.vision_range = stats["vision_range"]

    @property
    def name(self) -> str:
        return self.building_type.value.title()

    def generate_income(self) -> int:
        return self.gold_income if self.owner is not None else 0

    def can_recruit(self) -> bool:
        return self.building_type in {BuildingType.CASTLE, BuildingType.BARRACKS} and self.owner is not None

    def get_recruitable_units(self) -> list[UnitType]:
        if self.building_type == BuildingType.CASTLE:
            return [UnitType.WARRIOR, UnitType.ARCHER, UnitType.MAGE]
        if self.building_type == BuildingType.BARRACKS:
            return [UnitType.WARRIOR, UnitType.ARCHER, UnitType.CAVALRY, UnitType.CATAPULT]
        return []
