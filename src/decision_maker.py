from dataclasses import dataclass
from typing import Dict

from context import Context
from models import *
from utils import *
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
    def make_decision_petru(self, state: State) -> HourRequestDto:
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

                    use = max(0, min(capacity, current, wanted * BIAS[cls]))
                    # use = max(0, min(capacity, wanted))
                    # use = 0

                    setattr(pca, pca_attr, use)
                    setattr(airport, stock_attr, current - use)

                    flight.load[cls] = use
                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_processing(
                        state.time,
                        flight.load[cls],
                        cls,
                        flight.destination_airport_id
                    )
                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        # send stuff
        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads

        return resp

    def make_decision_floron(self, state: State) -> HourRequestDto:
        loads = []

        # --- STRATEGY CONFIGURATION ---
        SIMULATION_END_HOUR = 720  # 30 days * 24 hours
        # Stop sending buffer stock 72 hours (3 days) before end
        # This allows existing outstation stocks to be consumed by return flights
        DRAIN_MODE_START_HOUR = 720

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

                    bias_val = BIAS[cls]
                    # --- OPTIMIZATION LOGIC ---
                    if state.time >= DRAIN_MODE_START_HOUR:
                        # End Game Phase: STRICT DEMAND
                        # Only load exactly what is needed for passengers.
                        # This stops accumulating stock at destinations and minimizes
                        # kits in transit/processing when the game ends.
                        demand = 0
                    else:
                        # Normal Phase: BUFFERING
                        # Use the bias to push extra kits to outstations

                        demand = wanted * bias_val

                    # Calculate use, ensuring it's an integer
                    use = int(max(0, min(capacity, current, demand)))
                    # --------------------------

                    setattr(pca, pca_attr, use)
                    setattr(airport, stock_attr, current - use)

                    flight.load[cls] = use
                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_processing(
                        state.time,
                        flight.load[cls],
                        cls,
                        flight.destination_airport_id
                    )
                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        # send stuff
        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads

        return resp

    def make_decision(self, state: State) -> HourRequestDto:
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

                    use = max(0, min(capacity, current, wanted * BIAS[cls]))
                    # use = max(0, min(capacity, wanted))
                    # use = 0

                    setattr(pca, pca_attr, use)
                    setattr(airport, stock_attr, current - use)

                    flight.load[cls] = use
                loads.append(FlightLoadDto(flight.flight_id, pca))

            elif flight.status == FlightStatus.LANDED:
                if not flight.load:
                    continue
                for cls in CLASS_KEYS:
                    state.inventory.insert_processing(
                        state.time,
                        flight.load[cls],
                        cls,
                        flight.destination_airport_id
                    )
                flight.load = {}

            elif flight.status == FlightStatus.SCHEDULED:
                continue

        # send stuff
        day, hour = decode_time(state.time)
        resp = HourRequestDto(day, hour)
        resp.flight_loads = loads

        return resp

    """
    def make_decision_floron(self, state: State) -> HourRequestDto:
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

                    if cls == CLASS_KEYS[0] or cls == CLASS_KEYS[1] or cls == CLASS_KEYS[2]:
                        use = max(0, min(capacity, current, wanted))
                    else:
                        use = 0
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

        fixed_purchase = PerClassAmount()
        fixed_purchase.first = 1 if state.time % 24 == 0 else 0  # ~Daily demand / 24
        fixed_purchase.business = 1 if state.time % 24 == 0 else 0  # ~Daily demand / 24
        fixed_purchase.premium_economy = 0  # ~Daily demand / 24
        fixed_purchase.economy = 0  # ~Daily demand / 24


        resp.kit_purchasing_orders = fixed_purchase

        return resp
    
    
    """
    
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




