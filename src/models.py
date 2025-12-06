from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

CLASSES = ["first", "business", "premiumEconomy", "economy"]


class FlightStatus(Enum):
    SCHEDULED = 1
    CHECKED_IN = 2
    LANDED = 3


@dataclass
class Aircraft:
    type_id: str
    type_code: str

    first_class_seats: int
    business_seats: int
    premium_economy_seats: int
    economy_seats: int

    cost_per_kg_per_km: float

    first_class_kits_capacity: int
    business_kits_capacity: int
    premium_economy_kits_capacity: int
    economy_kits_capacity: int


@dataclass
class Flight:
    status: FlightStatus

    flight_number: str
    flight_id: str

    origin_airport_id: str
    destination_airport_id: str

    # hour + day * 24
    departure: int
    arrival: int

    # keys: first, business, premiumEconomy, economy
    passengers: dict[str, int]

    aircraft_id: str

    load: Optional[dict[str, int]] = None


@dataclass
class PlannedFlight:
    depart_code: str
    arrival_code: str

    scheduled_depart: int
    scheduled_arrival: int

    distance: int
    flight_days: list[int]


@dataclass
class Airport:
    id: str
    code: str
    name: str

    first_processing_time: int
    business_processing_time: int
    premium_economy_processing_time: int
    economy_processing_time: int

    first_processing_cost: float
    business_processing_cost: float
    premium_economy_cost: float
    economy_processing_cost: float

    first_loading_cost: float
    business_loading_cost: float
    premium_economy_loading_cost: float
    economy_loading_cost: float

    first_stock: int
    business_stock: int
    premium_economy_stock: int
    economy_stock: int

    first_capacity: int
    business_capacity: int
    premium_economy_capacity: int
    economy_capacity: int


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
            "economy": self.economy,
        }


@dataclass
class FlightLoadDto:
    flight_id: str
    loaded_kits: PerClassAmount

    def to_dict(self):
        return {
            "flightId": str(self.flight_id),
            "loadedKits": self.loaded_kits.to_dict(),
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
            "flightLoads": [fl.to_dict() for fl in self.flight_loads],
        }
        if self.kit_purchasing_orders:
            data["kitPurchasingOrders"] = self.kit_purchasing_orders.to_dict()
        return data
