from mm_crypto_utils import ConfigValidators


def test_proxies():
    assert ConfigValidators.proxies()(None) == []
    assert ConfigValidators.proxies()("") == []
    assert ConfigValidators.proxies()("p1") == ["p1"]
    assert ConfigValidators.proxies()("p1\n p2 ") == ["p1", "p2"]
