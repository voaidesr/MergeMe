from dataclasses import dataclass, field
from utils import *
from context import Context
# HERE WE IMPLEMENT THE PROCESSING DICT

@dataclass
class Inventory:
    context: Context
    processing_dict: dict[int, list[tuple]] = field(default_factory=dict)

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

    # process hour
    def process(self, hour: int) -> None:
        if hour not in self.processing_dict:
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