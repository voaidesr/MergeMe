from dataclasses import dataclass
from typing import Dict

from context import Context
from models import *
from utils import encode_time, decode_time, CLASS_KEYS
from state import State

@dataclass
class DecisionMaker:
    context: Context

    def __post_init__(self):
        pass


    def empty_decision(self, state: State) -> HourRequestDto:
        day, hour  = decode_time(state.time)
        return HourRequestDto(day, hour)

    #TODO
    def make_decision(self, state: State) -> HourRequestDto:
        loads = []

        # Maps class keys → attribute names for each object involved
        STOCK_FIELDS = {
            "first": "first_stock",
            "business": "business_stock",
            "premiumEconomy": "premium_economy_stock",
            "economy": "economy_stock",
        }

        CAPACITY_FIELDS = {
            "first": "first_class_kits_capacity",
            "business": "business_kits_capacity",
            "premiumEconomy": "premium_economy_kits_capacity",
            "economy": "economy_kits_capacity",
        }

        PCA_FIELDS = {
            "first": "first",
            "business": "business",
            "premiumEconomy": "premium_economy",
            "economy": "economy",
        }

        for flight in state.flights_dict.values():
            if flight.status == FlightStatus.CHECKED_IN:
                if flight.load:
                    continue

                pca = PerClassAmount()
                origin_id = flight.origin_airport_id
                aircraft_id = flight.aircraft_id
                airport = self.context.airport_dict[origin_id]
                aircraft = self.context.aircraft_dict[aircraft_id]

                for cls in CLASS_KEYS:
                    wanted = flight.passengers[cls]

                    stock_attr = STOCK_FIELDS[cls]
                    capacity_attr = CAPACITY_FIELDS[cls]
                    pca_attr = PCA_FIELDS[cls]

                    current = getattr(airport, stock_attr)
                    capacity = getattr(aircraft, capacity_attr)

                    use = max(0, min(capacity, current, wanted))

                    setattr(pca, pca_attr, use)
                    setattr(airport, stock_attr, current - use)

                    flight.load[cls] = use
                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_future(
                        state.time,
                        flight.load[cls],
                        cls,
                        flight.destination_airport_id
                    )
                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads
        return resp

    
    
    
    """
    def naive_decision(self, state: State) -> HourRequestDto:
        loads = []

        pca_purchase = PerClassAmount()
        pca_purchase.first = 1
        pca_purchase.business = 20
        pca_purchase.premium_economy = 30
        pca_purchase.economy = 40

        for fid in state.flights_dict:
            flight = state.flights_dict[fid]

            if flight.status == FlightStatus.CHECKED_IN:
                pca = PerClassAmount()

                origin = flight.origin_airport_id


                for cls in CLASS_KEYS:
                    cnt = flight.passengers[cls]
                    available = invent_obj.available[cls]

                    use = min(cnt, available)

                    match cls:
                        case "first":
                            pca.first = use

                        case "business":
                            pca.business = use

                        case "premiumEconomy":
                            pca.premium_economy = use

                        case "economy":
                            pca.economy = use


                    invent_obj.available[cls] -= use

                loads.append(FlightLoadDto(flight.flight_id, pca))


            elif flight.status == FlightStatus.LANDED:
                continue

            else:
                continue

        # Moved OUTSIDE the loop
        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads

        if state.time % (7*24) == 0:
            resp.kit_purchasing_orders = pca_purchase


        return resp
    """




