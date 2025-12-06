from dataclasses import dataclass
from typing import Dict

from context import Context
from models import *
from utils import encode_time, decode_time, CLASS_KEYS
from state import State


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

    def __post_init__(self):
        pass


    def empty_decision(self, state: State) -> HourRequestDto:
        day, hour  = decode_time(state.time)
        return HourRequestDto(day, hour)

    #TODO
    def make_decision(self, state: State) -> HourRequestDto:
        loads = []

        for fid in state.flights_dict:
            flight = state.flights_dict[fid]

            if flight.status == FlightStatus.CHECKED_IN:
                if flight.load:
                    continue
                pca = PerClassAmount()


                for cls in CLASS_KEYS:
                    wanted = flight.passengers[cls]

                    # TODO: implement formula to calculate how many kits to load
                    #available = invent_obj.available[cls]
                    #use = max(0, min(wanted, current, capacity))

                    origin_id = flight.origin_airport_id
                    aircraft_id = flight.aircraft_id
                    aicraft_capacity = self.context.aircraft_dict[aircraft_id]
                    match cls:
                        case "first":
                            current = self.context.airport_dict[origin_id].first_stock
                            capacity = aicraft_capacity.first_class_kits_capacity
                            use = max(0, min(capacity, current, wanted))
                            pca.first = use
                            self.context.airport_dict[origin_id].first_stock -= use

                        case "business":
                            current = self.context.airport_dict[origin_id].business_stock
                            capacity = aicraft_capacity.business_kits_capacity
                            use = max(0, min(capacity, current, wanted))
                            pca.business = use
                            self.context.airport_dict[origin_id].business_stock -= use

                        case "premiumEconomy":
                            current = self.context.airport_dict[origin_id].premium_economy_stock
                            capacity = aicraft_capacity.premium_economy_kits_capacity
                            use = max(0, min(capacity, current, wanted))
                            pca.premium_economy = use
                            self.context.airport_dict[origin_id].premium_economy_stock -= use

                        case "economy":
                            current = self.context.airport_dict[origin_id].economy_stock
                            capacity = aicraft_capacity.economy_kits_capacity
                            use = max(0, min(capacity, current, wanted))
                            pca.economy = use
                            self.context.airport_dict[origin_id].economy_stock -= use

                    flight.load[cls] = use

                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_future(state.time, flight.load[cls], cls, flight.destination_airport_id)

                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        # TODO: buy order logic

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




