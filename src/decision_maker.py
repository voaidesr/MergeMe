from dataclasses import dataclass
from utils import HourRequestDto, PerClassAmount, decode_time, FlightLoadDto
from models import FlightStatus, CLASSES
from state import State
from context import Context

@dataclass
class DecisionMaker:
    context: Context
    
    def __post_init__(self):
        pass
    
    def empty_decision(self, state: State) -> HourRequestDto:
        day, hour  = decode_time(state.time)
        return HourRequestDto(day, hour)
    
    def naive_decision(self, state: State) -> HourRequestDto:
        loads= []
        for fid in state.flights_dict:
            flight = state.flights_dict[fid]
            
            if flight.status == FlightStatus.CHECKED_IN:
                # incarci kit-uri cat ai nevoie
                pca = PerClassAmount()
                
                origin = flight.origin_airport_id
                
                invent = state.inventory_manager
                invent_obj = invent.inventories[origin]
                
                for cls in CLASSES:  
                    cnt = flight.passengers[cls]
                    match cls:
                        case 'first':
                            #pca.first = 0
                            if cnt > invent_obj.available['first']:
                                pca.first = max(0, invent_obj.available['first'])
                                invent_obj.available['first'] -= pca.first
                            else:
                                pca.first = cnt
                                invent_obj.available['first'] -= cnt
                                
                        case 'business':
                            #pca.business = 0
                            if cnt > invent_obj.available['business']:
                                pca.business = max(0, invent_obj.available['business'])
                                invent_obj.available['business'] -= pca.business
                            else:
                                pca.business = cnt
                                invent_obj.available['business'] -= cnt
                        case 'premiumEconomy':
                            #pca.premium_economy = 0
                            if cnt > invent_obj.available['premiumEconomy']:
                                pca.premium_economy = max(0, invent_obj.available['premiumEconomy'])
                                invent_obj.available['premiumEconomy'] -= pca.premium_economy
                            else:
                                pca.premium_economy = cnt
                                invent_obj.available['premiumEconomy'] -= cnt
                        case 'economy':
                            # pca.economy = 0
                            if cnt > invent_obj.available['economy']:
                                pca.economy = max(0, invent_obj.available['economy'])
                                invent_obj.available['economy'] -= pca.economy
                            else:
                                pca.economy = cnt
                                invent_obj.available['economy'] -= cnt
                            
                fldto = FlightLoadDto(flight.flight_id, pca)
                loads.append(fldto)
            
            elif flight.status == FlightStatus.LANDED:
                # bagi kit-urile in procesare
                continue
            
            else:
                continue
            
        # return hour request
        day, hour  = decode_time(state.time)
        hour_request = HourRequestDto(day, hour)
        hour_request.flight_loads = loads
        return hour_request