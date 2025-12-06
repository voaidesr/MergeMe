from typing import Dict
from models import *
from context import Context
from utils import encode_time
from models import Aircraft, Airport
from inventory import Inventory

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

    def __post_init__(self):
        self.inventory: Inventory = Inventory(self.context)

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

            aircraft_id = flight_entry.get("aircraftType", "")

            origin_code = self.context.airport_id_to_code.get(flight_entry["originAirport"], flight_entry["originAirport"])
            dest_code = self.context.airport_id_to_code.get(flight_entry["destinationAirport"], flight_entry["destinationAirport"])

            # --- 3. Check for Existing Flight and Update/Create ---
            if flight_id in self.flights_dict:
                existing_flight = self.flights_dict[flight_id]

                # Typically, only certain attributes are updated, like status, times, and passengers.
                # We assume flight number, airport IDs, and aircraft ID remain constant in an update.
                existing_flight.status = status_enum
                existing_flight.origin_airport_id = origin_code
                existing_flight.destination_airport_id = dest_code
                existing_flight.departure = departure_time
                existing_flight.arrival = arrival_time
                existing_flight.passengers = flight_entry["passengers"]

            else:
                # Flight does not exist: Create and store a new Flight object
                new_flight = Flight(
                    status=status_enum,
                    flight_number=flight_entry["flightNumber"],
                    flight_id=flight_id,
                    origin_airport_id=origin_code,
                    destination_airport_id=dest_code,
                    departure=departure_time,
                    arrival=arrival_time,
                    passengers=flight_entry["passengers"],
                    aircraft_id = aircraft_id,
                    distance= flight_entry["distance"]
                )

                # Store the new flight
                self.flights_dict[new_flight.flight_id] = new_flight


    def get_penalties(self, response):
        return response['penalties']

    def init_update_state(self):
        self.inventory.process(self.time)

    def update_state(self, response: dict):
        # update based on response
        self.update_flights(response)

        # the state represents the next round (hour)
        self.time += 1
