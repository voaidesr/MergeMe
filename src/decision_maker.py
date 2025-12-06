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
        #CHECKED_IN

        #LANDED
        pass
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




