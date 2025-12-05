
from dataclasses import dataclass, field
from typing import List, Optional
import uuid

@dataclass
class PerClassAmount:
    first: int = 0
    business: int = 0
    premium_economy: int = 0
    economy: int = 0

    def to_dict(self):
        return {
            "first": self.first,
            "business": self.business,
            "premiumEconomy": self.premium_economy,
            "economy": self.economy
        }

@dataclass
class FlightLoadDto:
    flight_id: uuid.UUID
    loaded_kits: PerClassAmount

    def to_dict(self):
        return {
            "flightId": str(self.flight_id),
            "loadedKits": self.loaded_kits.to_dict()
        }

@dataclass
class HourRequestDto:
    day: int
    hour: int
    flight_loads: List[FlightLoadDto] = field(default_factory=list)
    kit_purchasing_orders: Optional[PerClassAmount] = None

    def to_dict(self):
        data = {
            "day": self.day,
            "hour": self.hour,
            "flightLoads": [fl.to_dict() for fl in self.flight_loads]
        }
        if self.kit_purchasing_orders:
            data["kitPurchasingOrders"] = self.kit_purchasing_orders.to_dict()
        return data
