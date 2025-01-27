from decimal import Decimal

from mm_crypto_utils.calcs import calc_decimal_value


def test_calc_decimal_value():
    assert calc_decimal_value("123") == Decimal("123")
    assert calc_decimal_value("124.1") == Decimal("124.1")
    assert Decimal("1") <= calc_decimal_value("random(1,3)") <= Decimal("3")
