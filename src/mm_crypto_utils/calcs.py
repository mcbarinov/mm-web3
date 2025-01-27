from decimal import Decimal

from mm_std import random_decimal


def calc_decimal_value(value: str) -> Decimal:
    value = value.lower().strip()
    if value.startswith("random(") and value.endswith(")"):
        arr = value.lstrip("random(").rstrip(")").split(",")
        if len(arr) != 2:
            raise ValueError(f"wrong value, random part: {value}")
        from_value = Decimal(arr[0])
        to_value = Decimal(arr[1])
        if from_value > to_value:
            raise ValueError(f"wrong value, random part: {value}")
        return random_decimal(from_value, to_value)
    return Decimal(value)
