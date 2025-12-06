
from typing import Tuple
# CONSTANTS

CLASS_KEYS = ("first", "business", "premiumEconomy", "economy")

def encode_time(days: int, hours: int) -> int:
    return days * 24 + hours

def decode_time(time: int) -> Tuple[int, int]:
    return (time // 24, time % 24)
