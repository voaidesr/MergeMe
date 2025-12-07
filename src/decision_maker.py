from dataclasses import dataclass
from typing import Dict

from context import Context
from models import *
from utils import *
from state import State


"""
Decision maker = makes decisions for a given dynamic state.
A strategy is implemented here to give an 'optimal' response

"""


@dataclass
class DecisionMaker:
    context: Context

    def __post_init__(self):
        pass

    def empty_decision(self, state: State) -> HourRequestDto:
        # empty decision = do nothing
        day, hour = decode_time(state.time)
        return HourRequestDto(day, hour)

    def make_decision(self, state: State) -> HourRequestDto:
        # our strategy
        loads = []
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

                    # we decide here which customers to satisfy based on a BIAS.
                    use = max(0, min(capacity, current, wanted * BIAS[cls]))
                    setattr(pca, pca_attr, use)
                    setattr(airport, stock_attr, current - use)
                    flight.load[cls] = use

                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_processing(
                        state.time, flight.load[cls], cls, flight.destination_airport_id
                    )
                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        # send stuff
        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads
        return resp
