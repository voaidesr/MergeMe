from models import *
import pandas as pd
from typing import Optional, Dict


@dataclass
class App:
    aircraft_dict: Dict[str, Aircraft] = field(default_factory=dict)
    airport_dict: Dict[str, Airport] = field(default_factory=dict)

    def parse_aircraft(self, path: str) -> None:
        """
        Parses aircraft_types.csv using pandas and populates aircraft_dict.
        """
        try:
            df = pd.read_csv(path, sep=';')

            for _, row in df.iterrows():
                aircraft = Aircraft(
                    type_id=row['id'],
                    type_code=row['type_code'],
                    first_class_seats=int(row['first_class_seats']),
                    business_seats=int(row['business_seats']),
                    premium_economy_seats=int(row['premium_economy_seats']),
                    economy_seats=int(row['economy_seats']),
                    cost_per_kg_per_km=float(row['cost_per_kg_per_km']),
                    first_class_kits_capacity=int(row['first_class_kits_capacity']),
                    business_kits_capacity=int(row['business_kits_capacity']),
                    premium_economy_kits_capacity=int(row['premium_economy_kits_capacity']),
                    economy_kits_capacity=int(row['economy_kits_capacity'])
                )
                self.aircraft_dict[aircraft.type_code] = aircraft

            print(f"Loaded {len(self.aircraft_dict)} aircraft types.")

        except FileNotFoundError:
            print(f"Error: Aircraft file not found at {path}")
        except Exception as e:
            print(f"Error parsing aircraft: {e}")

    def parse_airports(self, path: str) -> None:
        """
        Parses airports_with_stocks.csv using pandas and populates airport_dict.
        """
        try:
            df = pd.read_csv(path, sep=';')

            for _, row in df.iterrows():
                # Mapping CSV columns to dataclass fields
                airport = Airport(
                    id=row['id'],
                    code=row['code'],
                    name=row['name'],

                    first_processing_time=int(row['first_processing_time']),
                    business_processing_time=int(row['business_processing_time']),
                    premium_economy_processing_time=int(row['premium_economy_processing_time']),
                    economy_processing_time=int(row['economy_processing_time']),

                    first_processing_cost=float(row['first_processing_cost']),
                    business_processing_cost=float(row['business_processing_cost']),
                    # Note: CSV column is premium_economy_processing_cost
                    premium_economy_cost=float(row['premium_economy_processing_cost']),
                    economy_processing_cost=float(row['economy_processing_cost']),

                    first_loading_cost=float(row['first_loading_cost']),
                    business_loading_cost=float(row['business_loading_cost']),
                    premium_economy_loading_cost=float(row['premium_economy_loading_cost']),
                    economy_loading_cost=float(row['economy_loading_cost']),

                    # Stock Mappings
                    first_stock=int(row['initial_fc_stock']),
                    business_stock=int(row['initial_bc_stock']),
                    premium_economy_stock=int(row['initial_pe_stock']),
                    economy_stock=int(row['initial_ec_stock']),

                    # Capacity Mappings
                    first_capacity=int(row['capacity_fc']),
                    business_capacity=int(row['capacity_bc']),
                    premium_economy_capacity=int(row['capacity_pe']),
                    economy_capacity=int(row['capacity_ec'])
                )
                self.airport_dict[airport.code] = airport

            print(f"Loaded {len(self.airport_dict)} airports.")

        except FileNotFoundError:
            print(f"Error: Airport file not found at {path}")
        except Exception as e:
            print(f"Error parsing airports: {e}")

    def initialize(self):
        # Example of how you might use the parse methods
        self.parse_aircraft('../data/aircraft_types.csv')
        self.parse_airports('../data/airports_with_stocks.csv')

        print(self.aircraft_dict)
        print(self.airport_dict)