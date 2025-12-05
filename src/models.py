from dataclasses import dataclass, field
from typing import List, Optional
import uuid
from enum import Enum

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


@dataclass
class Airport:
    id: str
    code: str
    name:str

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


# -- TEST CLASSES