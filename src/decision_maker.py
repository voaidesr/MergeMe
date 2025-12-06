from dataclasses import dataclass
from utils import HourRequestDto, decode_time

from state import State
from context import Context

@dataclass
class DecisionMaker:
    context: Context
    
    def __post_init__(self):
        pass
    
    def make_decision(self, state: State) -> HourRequestDto:
        day, hour  = decode_time(state.time)
        hour_request = HourRequestDto(day, hour)
        
        return hour_request