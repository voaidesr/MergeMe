from typing import Dict
from models import *
from context import Context
from utils import encode_time
from models import Aircraft, Airport

from inventory import InventoryManager
from processing_queue import KitProcessingQueue

"""
State object:
Data that changes every hour.
- Schedules
- Actual arrival times
- Etc.
"""

@dataclass
class State:
    context: Context
    flights_dict: Dict[str, Flight] = field(default_factory=dict)
    time: int = 0
    
    inventory_manager: Optional[InventoryManager] = None
    processing_queue: Optional[KitProcessingQueue] = None
    
    def __post_init__(self):
        self.inventory_manager = InventoryManager.from_airports(self.context.airport_dict)
        
    def complete_processing_tick(self) -> None:
        """
        Advance processing by one hour and move finished kits into inventory.
        """
        if not self.processing_queue or not self.inventory_manager:
            return
        violations = self.processing_queue.apply_tick(self.inventory_manager, hours=1)
        if violations:
            print("Processing violations:", violations)
            
    def _processing_times_for_airport(self, airport_code: str) -> Dict[str, int]:
        airport = self.context.airport_dict.get(airport_code)
        if not airport:
            return {}
        return {
            "first": airport.first_processing_time,
            "business": airport.business_processing_time,
            "premiumEconomy": airport.premium_economy_processing_time,
            "economy": airport.economy_processing_time,
        }

    def enqueue_kits_for_processing(self, airport_code: str, amounts: Dict[str, int]) -> None:
        """
        Call this when kits arrive at an airport; they will become available after processing time.
        """
        if not self.processing_queue:
            return
        processing_times = self._processing_times_for_airport(airport_code)
        self.processing_queue.add_batch(airport_code, amounts, processing_times)
    
    def update_flights(self, response:dict):
        flights = response["flightUpdates"]
        for flight_entry in flights:
            # --- 1. Calculate Time ---
            departure_days_elapsed = flight_entry["departure"]["day"] - 1
            arrival_days_elapsed = flight_entry["arrival"]["day"] - 1

            departure_time = encode_time(
                days=departure_days_elapsed,
                hours=flight_entry["departure"]["hour"]
            )

            arrival_time = encode_time(
                days=arrival_days_elapsed,
                hours=flight_entry["arrival"]["hour"]
            )

            # --- 2. Convert Status and Get Aircraft ID ---
            status_enum = FlightStatus[flight_entry["eventType"]]
            flight_id = flight_entry["flightId"]

            aircraft_id = ''
            for id in self.context.aircraft_dict:
                if flight_entry["aircraftType"] ==  self.context.aircraft_dict[id]:
                    aircraft_id = id
                    break

            # --- 3. Check for Existing Flight and Update/Create ---
            if flight_id in self.flights_dict:
                existing_flight = self.flights_dict[flight_id]

                # Typically, only certain attributes are updated, like status, times, and passengers.
                # We assume flight number, airport IDs, and aircraft ID remain constant in an update.
                existing_flight.status = status_enum
                existing_flight.departure = departure_time
                existing_flight.arrival = arrival_time
                existing_flight.passengers = flight_entry["passengers"]

            else:
                # Flight does not exist: Create and store a new Flight object
                new_flight = Flight(
                    status=status_enum,
                    flight_number=flight_entry["flightNumber"],
                    flight_id=flight_id,
                    origin_airport_id=flight_entry["originAirport"],
                    destination_airport_id=flight_entry["destinationAirport"],
                    departure=departure_time,
                    arrival=arrival_time,
                    passengers=flight_entry["passengers"],
                    aircraft_id = aircraft_id # Link to the aircraft ID
                )

                # Store the new flight
                self.flights_dict[new_flight.flight_id] = new_flight
    
    def update_state(self, response: dict):
        # update based on response
        self.update_flights(response)
        self.complete_processing_tick()
        
        # the state represents the next round (hour)        
        self.time += 1