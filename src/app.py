import os
import requests
from typing import Optional, Dict
from parser import Parser
from dotenv import load_dotenv
from api_client import ApiClient
from utils import HourRequestDto, decode_time, encode_time
from models import *
from inventory import InventoryManager


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@dataclass
class App:
    aircraft_dict: Dict[str, Aircraft] = field(default_factory=dict)
    airport_dict: Dict[str, Airport] = field(default_factory=dict)
    flights_dict: Dict[str, Flight] = field(default_factory=dict)
    inventory_manager: Optional[InventoryManager] = None

    def connect_api(self):
        load_dotenv()
        BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
        API_KEY = os.getenv("API_KEY")

        if not API_KEY:
            raise ValueError("API_KEY not found in .env file or environment variables.")
        
        # play with the api
        self.client = ApiClient(base_url=BASE_URL, api_key=API_KEY)    
        
        
    def initialize(self):
        # Connect the api
        self.connect_api()
        
        # Example of how you might use the parse methods
        parser = Parser()
        
        self.aircraft_dict = parser.parse_aircraft('../data/aircraft_types.csv')
        self.airport_dict = parser.parse_airports('../data/airports_with_stocks.csv')

        self.inventory_manager = InventoryManager.from_airports(self.airport_dict)

        if self.inventory_manager:
            print("Initial inventories: ")
            print(self.inventory_manager.snapshot())

        #print(self.aircraft_dict)
        #print(self.airport_dict)

    def update_flights(self, response):
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
            for id in self.aircraft_dict:
                if flight_entry["aircraftType"] ==  self.aircraft_dict[id]:
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

    def run(self):  
        try:
            self.client.start_session()
            stop_time, curr_time = 1, 0
            
            while curr_time < stop_time:
                day, hour = decode_time(curr_time)
                
                hour_request = HourRequestDto(day, hour)
                response = self.client.play_round(hour_request)
                
                self.update_flights(response)



                # f = open('response.json', 'w')
                # json_string = json.dumps(response, indent=3)
                # f.write(json_string)
                # f.close()
                # print(response["day"], response['hour'])
                
                print(f'-------------TIME {curr_time}---------------')
                for idx, flight_id in enumerate(self.flights_dict):
                    print(idx, self.flights_dict[flight_id].status)
                
                curr_time += 1

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} {e.response.reason}")
            print(e.response.json())
        except Exception as e:
            print(f"Error parsing airports: {e}")