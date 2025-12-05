from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional

from models import Airport

CLASS_KEYS = ("first", "business", "premiumEconomy", "economy")

@dataclass
class InventoryViolation:
    negative: int = 0
    over_capacity: int = 0

    def has_issue(self) -> bool:
        return self.negative > 0 or self.over_capacity > 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "negative": self.negative,
            "overCapacity": self.over_capacity,
        }


@dataclass
class InventoryRecord:
    available: Dict[str, int] = field(default_factory=dict)
    capacity: Dict[str, int] = field(default_factory=dict)

    def apply_delta(self, delta: Mapping[str, int]) -> Dict[str, InventoryViolation]:
        violations: Dict[str, InventoryViolation] = {}
        for kit_class in CLASS_KEYS:
            change = delta.get(kit_class, 0)
            if change == 0 and kit_class not in self.available:
                continue

            new_value = self.available.get(kit_class, 0) + change
            self.available[kit_class] = new_value

            violation = InventoryViolation()
            if new_value < 0:
                violation.negative = -new_value
            capacity_limit = self.capacity.get(kit_class)
            if capacity_limit is not None and capacity_limit >= 0 and new_value > capacity_limit:
                violation.over_capacity = new_value - capacity_limit

            if violation.has_issue():
                violations[kit_class] = violation

        return violations

    def snapshot(self) -> Dict[str, int]:
        return {k: self.available.get(k, 0) for k in CLASS_KEYS}


@dataclass
class InventoryManager:
    inventories: Dict[str, InventoryRecord] = field(default_factory=dict)

    @classmethod
    def from_airports(cls, airports: Mapping[str, Airport]) -> "InventoryManager":
        inventories: Dict[str, InventoryRecord] = {}
        for code, airport in airports.items():
            inventories[code] = InventoryRecord(
                available={
                    "first": airport.first_stock,
                    "business": airport.business_stock,
                    "premiumEconomy": airport.premium_economy_stock,
                    "economy": airport.economy_stock,
                },
                capacity={
                    "first": airport.first_capacity,
                    "business": airport.business_capacity,
                    "premiumEconomy": airport.premium_economy_capacity,
                    "economy": airport.economy_capacity,
                },
            )
        return cls(inventories=inventories)

    def apply_movements(self, movements: Mapping[str, Mapping[str, int]]) -> Dict[str, Dict[str, InventoryViolation]]:
        all_violations: Dict[str, Dict[str, InventoryViolation]] = {}
        for airport_code, delta in movements.items():
            record = self.inventories.get(airport_code)
            if not record:
                # Unknown airports can be handled later; ignore for now.
                continue
            violations = record.apply_delta(delta)
            if violations:
                all_violations[airport_code] = violations
        return all_violations

    def get(self, airport_code: str) -> Optional[InventoryRecord]:
        return self.inventories.get(airport_code)

    def snapshot(self) -> Dict[str, Dict[str, int]]:
        return {airport: record.snapshot() for airport, record in self.inventories.items()}
