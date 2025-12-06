from dataclasses import dataclass, field
from utils import *
from context import Context
# HERE WE IMPLEMENT THE PROCESSING DICT

@dataclass
class Inventory:
    context: Context
    processing_dict: dict[int, list[tuple]] = field(default_factory=dict)
    purchase_dict: dict[int, list[tuple]] = field(default_factory=dict)

    # insert entry
    def insert(self, hour: int, quantity: int, kit_type: str, airport_id: str) -> None:
        # direct insert at the given hour
        if hour not in self.processing_dict:
            self.processing_dict[hour] = []
        self.processing_dict[hour].append((quantity, kit_type, airport_id))

    def insert_processing(self, hour: int, quantity: int, kit_type: str, airport_id: str) -> None:
        # compute processing-time shift
        airport = self.context.airport_dict[airport_id]

        match kit_type:
            case 'first':
                time_delta = airport.first_processing_time
            case 'business':
                time_delta = airport.business_processing_time
            case 'premiumEconomy':
                time_delta = airport.premium_economy_processing_time
            case 'economy':
                time_delta = airport.economy_processing_time
            case _:
                raise ValueError("Kit type unrecognized: inventory")

        future_hour = hour + time_delta

        if future_hour not in self.processing_dict:
            self.processing_dict[future_hour] = []
        self.processing_dict[future_hour].append((quantity, kit_type, airport_id))

    def insert_buying(self, hour: int, quantity: int, kit_type: str, airport_id: str) -> None:
        if kit_type not in RLT:
            raise ValueError("Kit type unrecognized: buying")

        time_delta = RLT[kit_type]
        buy_hour = hour + time_delta

        if buy_hour not in self.processing_dict:
            self.processing_dict[buy_hour] = []
        self.processing_dict[buy_hour].append((quantity, kit_type, airport_id))

    def schedule_purchase(self, hour: int, quantity: int, kit_type: str, airport_id: str, lead_time_map: dict[str, int]) -> int:
        """
        Track a purchase so we can keep our local stock estimates aligned with what we order.
        Returns the hour when the kits will be available at the airport.
        """
        if quantity <= 0:
            return hour

        lead_time = lead_time_map.get(kit_type, 0)
        arrival_hour = hour + lead_time

        if arrival_hour not in self.purchase_dict:
            self.purchase_dict[arrival_hour] = []
        self.purchase_dict[arrival_hour].append((quantity, kit_type, airport_id))

        return arrival_hour

    # process hour
    def process(self, hour: int) -> None:
        if hour not in self.processing_dict:
            # purchases can still land even if no processing batch is due
            self._process_purchases(hour)
            return
        airport_dict = self.context.airport_dict
        for quantity, kit_type, airport_id in self.processing_dict[hour]:
            match kit_type: # we must check for going stock > quantity
                case 'first':
                    airport_dict[airport_id].first_stock += quantity
                case 'business':
                    airport_dict[airport_id].business_stock += quantity
                case 'premiumEconomy':
                    airport_dict[airport_id].premium_economy_stock += quantity
                case 'economy':
                    airport_dict[airport_id].economy_stock += quantity
                case _:
                    raise ValueError("Kit type unrecognized: inventory")

        self.processing_dict.pop(hour) # eliminate all entries
        self._process_purchases(hour)

    def _process_purchases(self, hour: int) -> None:
        """
        Deliver any outstanding purchase orders that arrive at the given hour.
        Keeps capacity in mind so we never overfill an airport.
        """
        if hour not in self.purchase_dict:
            return

        airport_dict = self.context.airport_dict
        arrivals = self.purchase_dict.pop(hour)

        for quantity, kit_type, airport_id in arrivals:
            airport = airport_dict[airport_id]
            match kit_type:
                case 'first':
                    capacity_left = max(0, airport.first_capacity - airport.first_stock)
                    airport.first_stock += min(capacity_left, quantity)
                case 'business':
                    capacity_left = max(0, airport.business_capacity - airport.business_stock)
                    airport.business_stock += min(capacity_left, quantity)
                case 'premiumEconomy':
                    capacity_left = max(0, airport.premium_economy_capacity - airport.premium_economy_stock)
                    airport.premium_economy_stock += min(capacity_left, quantity)
                case 'economy':
                    capacity_left = max(0, airport.economy_capacity - airport.economy_stock)
                    airport.economy_stock += min(capacity_left, quantity)
                case _:
                    raise ValueError("Kit type unrecognized: inventory")
