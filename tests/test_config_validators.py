from mm_crypto_utils import ConfigValidators


def test_proxies():
    assert ConfigValidators.proxies()(None) == []
    assert ConfigValidators.proxies()("") == []
    assert ConfigValidators.proxies()("p1") == ["p1"]
    assert ConfigValidators.proxies()("p1\n p2 ") == ["p1", "p2"]


def test_transfers():
    data = """
0x9B163ec908e4d42e46629Bd53DB3E5E2a1e3B29C 0xfcD85c77883171265e24b393f3a15C034bd3d406
0x92FC94382c8d878121b5DAe90dBBAf5f61DF4a1d 0x7Ff459eC8c2C91f5367ACf18a5583a166B653532 0.1balance-2eth
"""
    res = ConfigValidators.transfers(lambda _: True, to_lower=True)(data)
    assert len(res) == 2
    assert res[1].from_address == "0x92fc94382c8d878121b5dae90dbbaf5f61df4a1d"
    assert res[1].to_address == "0x7ff459ec8c2c91f5367acf18a5583a166b653532"
    assert res[1].value == "0.1balance-2eth"
