from dataclasses import field
from typing import Optional, Dict
from parser import Parser
from models import Aircraft, Airport, PlannedFlight
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
    aircraft_dict: Dict[str, Aircraft] = field(default_factory=dict) # key is aircraft_id
    airport_dict: Dict[str, Airport] = field(default_factory=dict) # key is airport_id
    planned_flights_dict: Dict[str, PlannedFlight] = field(default_factory=dict) # key is airport name
    airport_id_to_code: Dict[str, str] = field(default_factory=dict)
    
    
    def __post_init__(self):
        # parse and get initial data from the csv's
        parser = Parser()
        self.aircraft_dict = parser.parse_aircraft('../data/aircraft_types.csv')
        self.airport_dict = parser.parse_airports('../data/airports_with_stocks.csv')
        self.airport_id_to_code = {airport.id: code for code, airport in self.airport_dict.items()}
        
