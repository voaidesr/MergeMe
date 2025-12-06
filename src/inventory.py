from dataclasses import dataclass
from utils import CLASS_KEYS
from context import Context
# HERE WE IMPLEMENT THE PROCESSING DICT

@dataclass
class Inventory:
    context: Context
    processing_dict: dict[int, list[tuple]]

    # insert entry
    def insert(self, hour: int, quantity: int, kit_type: str, airport_id: str) -> None:
        if hour not in self.processing_dict:
            self.processing_dict[hour] = []
        self.processing_dict[hour].append((quantity, kit_type, airport_id))

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
                    airport_dict[airport_id].economy_capacity += quantity
                case _:
                    raise ValueError("Kit type unrecognized: inventory")