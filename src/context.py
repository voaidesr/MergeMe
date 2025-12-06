from dataclasses import field
from typing import Optional, Dict
from parser import Parser
from models import Aircraft, Airport
from inventory import InventoryManager
from dataclasses import dataclass
from utils import HourRequestDto


"""
Context = data from CSV that doesn't change every hour (every API call)
The data consists of:
Airports
Flight Schedule
Airplane types
Inventory (kits), etc..
"""

@dataclass
class Context:
    aircraft_dict: Dict[str, Aircraft] = field(default_factory=dict)
    airport_dict: Dict[str, Airport] = field(default_factory=dict)
    inventory_manager: Optional[InventoryManager] = None
    
    def __post_init__(self):
        # parse and get initial data from the csv's
        parser = Parser()
        self.aircraft_dict = parser.parse_aircraft('../data/aircraft_types.csv')
        self.airport_dict = parser.parse_airports('../data/airports_with_stocks.csv')
        self.inventory_manager = InventoryManager.from_airports(self.airport_dict)