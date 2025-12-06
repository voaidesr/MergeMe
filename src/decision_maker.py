from dataclasses import dataclass
from typing import Dict

from context import Context
from inventory import CLASS_KEYS
import inventory
from models import FlightStatus
from state import State
from utils import FlightLoadDto, HourRequestDto, PerClassAmount, decode_time


# get the capacities for each aircraft for each class
def _class_caps(aircraft) -> Dict[str, int]:
    return {
        "first": getattr(aircraft, "first_class_kits_capacity", 0),
        "business": getattr(aircraft, "business_kits_capacity", 0),
        "premiumEconomy": getattr(aircraft, "premium_economy_kits_capacity", 0),
        "economy": getattr(aircraft, "economy_kits_capacity", 0),
    }


@dataclass
class DecisionMaker:
    context: Context

    def make_decision(self, state: State) -> HourRequestDto:
        """
        Naive decision: for CHECKED_IN flights, load up to min(demand, aircraft cap, available stock)
        and deduct from inventory immediately to keep state consistent.
        """
        day, hour = decode_time(state.time)

        inventory = state.inventory_manager

        flight_loads = []
        deltas_by_airport: Dict[str, Dict[str, int]] = {}
        sent_loads: Dict[str, Dict[str, int]] = {}

        for flight in state.flights_dict.values():
            if flight.status != FlightStatus.CHECKED_IN:
                continue
            if flight.flight_id in state.sent_loads:
                # Already loaded previously; skip reloading to avoid double counting in naive mode.
                continue

            origin = flight.origin_airport_id
            inv_record = inventory.get(origin)
            if not inv_record:
                continue

            aircraft = self.context.aircraft_dict.get(flight.aircraft_id)
            if not aircraft:
                continue
            caps = _class_caps(aircraft)

            passengers = flight.passengers or {}
            load_amounts: Dict[str, int] = {}
            for cls in CLASS_KEYS:
                demand = passengers.get(cls, 0)
                cap = caps.get(cls, 0)
                available = inv_record.available.get(cls, 0)
                load = max(0, min(demand, cap, available))
                if load > 0:
                    load_amounts[cls] = load

            if not load_amounts:
                continue

            flight_loads.append(
                FlightLoadDto(
                    flight_id=flight.flight_id,
                    loaded_kits=PerClassAmount(
                        first=load_amounts.get("first", 0),
                        business=load_amounts.get("business", 0),
                        premium_economy=load_amounts.get("premiumEconomy", 0),
                        economy=load_amounts.get("economy", 0),
                    ),
                )
            )

            sent_loads[flight.flight_id] = load_amounts
            airport_delta = deltas_by_airport.setdefault(origin, {})
            for cls, amt in load_amounts.items():
                airport_delta[cls] = airport_delta.get(cls, 0) - amt

        if deltas_by_airport:
            inventory.apply_movements(deltas_by_airport)
            state.sent_loads.update(sent_loads)

        return HourRequestDto(day, hour, flight_loads=flight_loads)
