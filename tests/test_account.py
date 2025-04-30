import pytest
from eth_account import Account

from mm_crypto.account import AddressToPrivate


def eth_get_account(private_key: str) -> str:
    acc = Account.from_key(private_key)
    return acc.address.lower()


def test_address_to_private_from_list():
    p1 = "0x82f61616142ce07f9396f8f4d44dda9981d9720b75022bcdfe8312ca810ef694"
    p2 = "0xa164d66c09e102e730bfbfd9f2de3ce4801ef7a24012c494764ff1b52af813c9"
    p3 = "0x6a369a041e02dff59ab8d7f50e4c8b70edea3cbb0f3faee97b13fa78c650ed2d"
    a1 = "0x80f5A75176cbf4Da0bFE384E6C83210f38A4FfCa".lower()
    a2 = "0x7d29Cfe669910A6c184F390396068d2eba27943E".lower()
    a3 = "0x51f81C8f577345df75c89f21e766fC998EfBfb7D".lower()

    res = AddressToPrivate.from_list([p1, p2, p3], eth_get_account)
    assert res == {a1.lower(): p1, a2.lower(): p2, a3.lower(): p3}

    with pytest.raises(ValueError):
        AddressToPrivate.from_list(["bad" + p1], eth_get_account)
