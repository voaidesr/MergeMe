from typing import Tuple
# CONSTANTS

CLASS_KEYS = ("first", "business", "premiumEconomy", "economy")

STOCK_FIELDS = {
    "first": "first_stock",
    "business": "business_stock",
    "premiumEconomy": "premium_economy_stock",
    "economy": "economy_stock",
}

CAPACITY_FIELDS = {
    "first": "first_class_kits_capacity",
    "business": "business_kits_capacity",
    "premiumEconomy": "premium_economy_kits_capacity",
    "economy": "economy_kits_capacity",
}

PCA_FIELDS = {
    "first": "first",
    "business": "business",
    "premiumEconomy": "premium_economy",
    "economy": "economy",
}

RLT = {
    "first": 48,
    "business": 36,
    "premiumEconomy": 24,
    "economy": 12,
}

BIAS = {
    "first": 0 / 100,
    "business": 0 / 100,
    "premiumEconomy": 100 / 100,
    "economy": 100 / 100,
}


def encode_time(days: int, hours: int) -> int:
    return days * 24 + hours


def decode_time(time: int) -> Tuple[int, int]:
    return (time // 24, time % 24)
