import random
from dataclasses import dataclass
from decimal import Decimal

from mm_std import random_decimal
from mm_std.str import split_on_plus_minus_tokens


@dataclass
class VarInt:
    name: str
    value: int

    def __post_init__(self) -> None:
        self.name = self.name.lower()
        if any(char.isspace() for char in self.name):
            raise ValueError(f"var.name contains spaces: {self.name}")


def calc_decimal_value(value: str) -> Decimal:
    """Calculate decimal value from string. It can be a random value."""
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


def calc_int_with_suffix_decimals(value: str, suffix_decimals: dict[str, int]) -> int:
    value = value.lower().strip()
    if value.startswith("-"):
        raise ValueError(f"negative value is illegal: {value}")
    if value.isdigit():
        return int(value)
    suffix_decimals = {k.lower(): v for k, v in suffix_decimals.items()}
    for suffix in suffix_decimals:
        if value.endswith(suffix):
            value = value.removesuffix(suffix)
            return int(Decimal(value) * 10 ** suffix_decimals[suffix])

    raise ValueError(f"illegal value: {value}")


def calc_int_expression(expression: str, var: VarInt | None = None, suffix_decimals: dict[str, int] | None = None) -> int:
    if not isinstance(expression, str):
        raise TypeError(f"expression is not str: {expression}")
    expression = expression.lower().strip()
    if suffix_decimals is None:
        suffix_decimals = {}
    suffix_decimals = {k.lower(): v for k, v in suffix_decimals.items()}
    if var is not None and var.name in suffix_decimals:
        raise ValueError(f"var.name in suffix_decimals: {var.name}")

    try:
        result = 0
        for token in split_on_plus_minus_tokens(expression.lower()):
            operator = token[0]
            item = token[1:]
            suffix = get_suffix(item, suffix_decimals)
            if item.isdigit():
                item_value = int(item)
            elif suffix is not None:
                item_value = calc_int_with_suffix_decimals(item, suffix_decimals)
            elif var is not None and item.endswith(var.name):
                item = item.removesuffix(var.name)
                k = Decimal(item) if item else Decimal(1)
                item_value = int(k * var.value)
            elif item.startswith("random(") and item.endswith(")"):
                item = item.lstrip("random(").rstrip(")")
                arr = item.split(",")
                if len(arr) != 2:
                    raise ValueError(f"illegal expression, random part: {expression}")  # noqa: TRY301
                from_value = calc_int_with_suffix_decimals(arr[0], suffix_decimals)
                to_value = calc_int_with_suffix_decimals(arr[1], suffix_decimals)
                if from_value > to_value:
                    raise ValueError(f"illegal expression, random from_value > to_value: {expression}")  # noqa: TRY301
                item_value = random.randint(from_value, to_value)
            else:
                raise ValueError(f"illegal: {expression}")  # noqa: TRY301

            if operator == "+":
                result += item_value
            if operator == "-":
                result -= item_value

        return result  # noqa: TRY300
    except Exception as e:
        raise ValueError(e) from e


def get_suffix(item: str, suffix_decimals: dict[str, int]) -> str | None:
    for suffix in suffix_decimals:
        if item.endswith(suffix):
            return suffix
    return None


def has_decimals_suffix(expression: str) -> bool:
    return any(expression.endswith(suffix) for suffix in ["eth", "ether", "gwei", "t"])
