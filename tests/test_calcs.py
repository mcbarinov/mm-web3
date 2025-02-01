from decimal import Decimal

import pytest

from mm_crypto_utils.calcs import calc_decimal_value, calc_int_expression, calc_int_with_suffix_decimals


def test_calc_decimal_expression():
    assert calc_decimal_value("123") == Decimal("123")
    assert calc_decimal_value("-124.1") == Decimal("-124.1")
    assert Decimal("1") <= calc_decimal_value("random(1,3)") <= Decimal("3")


def test_calc_int_with_suffix_decimals():
    assert calc_int_with_suffix_decimals("123", {}) == 123
    assert calc_int_with_suffix_decimals("1.12 eth", {"eth": 18}) == 1120000000000000000
    with pytest.raises(ValueError):
        calc_int_with_suffix_decimals("-1.12gwei", {"gwei": 9})


def test_calc_int_expression():
    suffix_decimals = {"eth": 18, "gwei": 9, "t": 6}
    assert calc_int_expression("100") == 100
    assert calc_int_expression("10 + 2 - 5") == 7
    assert calc_int_expression("10 - random(2,2)") == 8
    assert calc_int_expression("10gwei - random(2gwei,2gwei)", suffix_decimals=suffix_decimals) == 8000000000
    assert calc_int_expression("1.5estimate + 1", var_value=10, var_name="estimate") == 16

    with pytest.raises(ValueError):
        calc_int_expression("fff")
    with pytest.raises(ValueError):
        calc_int_expression("random(3,1)")
    with pytest.raises(ValueError):
        calc_int_expression("1.1gg")
    with pytest.raises(ValueError):
        calc_int_expression("1.5eth", suffix_decimals=suffix_decimals, var_name="eth", var_value=10)
    with pytest.raises(ValueError):
        calc_int_expression("1.5base", suffix_decimals=suffix_decimals, var_name="base")
