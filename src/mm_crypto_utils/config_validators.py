import os
from collections.abc import Callable
from pathlib import Path

import pydash
from mm_std import Err, str_to_list
from pydantic import BaseModel

from mm_crypto_utils import calc_decimal_value, calc_int_expression
from mm_crypto_utils.account import AddressToPrivate
from mm_crypto_utils.calcs import VarInt
from mm_crypto_utils.proxy import fetch_proxies

type IsAddress = Callable[[str], bool]


class TxRoute(BaseModel):
    from_address: str
    to_address: str

    @property
    def log_prefix(self) -> str:
        return f"{self.from_address}->{self.to_address}"


class ConfigValidators:
    @staticmethod
    def routes(is_address: IsAddress, to_lower: bool = False) -> Callable[[str], list[TxRoute]]:
        def validator(v: str) -> list[TxRoute]:
            result = []
            for line in str_to_list(v, remove_comments=True):
                if line.startswith("file:"):
                    arr = line.removeprefix("file:").strip().split()
                    if len(arr) != 2:
                        raise ValueError(f"illegal line in routes: {line}")
                    from_addresses = _read_lines_from_file(arr[0])
                    to_addresses = _read_lines_from_file(arr[1])
                    if len(from_addresses) != len(to_addresses):
                        raise ValueError(f"len(from_addresses) != len(to_addresses) for line: {line}")
                    result += [
                        TxRoute(from_address=from_address, to_address=to_address)
                        for from_address, to_address in zip(from_addresses, to_addresses, strict=True)
                    ]
                else:
                    arr = line.split()
                    if len(arr) != 2:
                        raise ValueError(f"illegal line in routes: {line}")
                    result.append(TxRoute(from_address=arr[0], to_address=arr[1]))

            if to_lower:
                result = [TxRoute(from_address=r.from_address.lower(), to_address=r.to_address.lower()) for r in result]

            for route in result:
                if not is_address(route.from_address):
                    raise ValueError(f"illegal address: {route.from_address}")
                if not is_address(route.to_address):
                    raise ValueError(f"illegal address: {route.to_address}")

            if not result:
                raise ValueError("routes is empty")

            return result

        return validator

    @staticmethod
    def proxies() -> Callable[[str], list[str]]:
        def validator(v: str) -> list[str]:
            result = []
            for line in str_to_list(v, unique=True, remove_comments=True):
                if line.startswith("url:"):
                    url = line.removeprefix("url:").strip()
                    res = fetch_proxies(url)
                    if isinstance(res, Err):
                        raise ValueError(f"Can't get proxies: {res.err}")
                    result += res.ok
                elif line.startswith("env_url:"):
                    env_var = line.removeprefix("env_url:").strip()
                    url = os.getenv(env_var) or ""
                    if not url:
                        raise ValueError(f"missing env var: {env_var}")
                    res = fetch_proxies(url)
                    if isinstance(res, Err):
                        raise ValueError(f"Can't get proxies: {res.err}")
                    result += res.ok
                elif line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    result += _read_lines_from_file(path)
                else:
                    result.append(line)

            return pydash.uniq(result)

        return validator

    @staticmethod
    def log_file() -> Callable[[Path], Path]:
        def validator(v: Path) -> Path:
            log_file = Path(v).expanduser()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch(exist_ok=True)
            if not log_file.is_file() or not os.access(log_file, os.W_OK):
                raise ValueError(f"wrong log path: {v}")
            return v

        return validator

    @staticmethod
    def nodes() -> Callable[[str], list[str]]:
        def validator(v: str) -> list[str]:
            return str_to_list(v, unique=True, remove_comments=True)

        return validator

    @staticmethod
    def address(is_address: IsAddress, to_lower: bool = False) -> Callable[[str], str]:
        def validator(v: str) -> str:
            if not is_address(v):
                raise ValueError(f"illegal address: {v}")
            if to_lower:
                return v.lower()
            return v

        return validator

    @staticmethod
    def addresses(unique: bool, to_lower: bool = False, is_address: IsAddress | None = None) -> Callable[[str], list[str]]:
        def validator(v: str) -> list[str]:
            addresses = str_to_list(v, unique=unique, remove_comments=True, lower=to_lower)
            if is_address:
                for address in addresses:
                    if not is_address(address):
                        raise ValueError(f"illegal address: {address}")
            return addresses

        return validator

    @staticmethod
    def private_keys(address_from_private: Callable[[str], str]) -> Callable[[str], AddressToPrivate]:
        def validator(v: str) -> AddressToPrivate:
            private_keys = []
            for line in str_to_list(v, unique=True, remove_comments=True):
                if line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    private_keys += _read_lines_from_file(path)
                else:
                    private_keys.append(line)

            return AddressToPrivate.from_list(private_keys, address_from_private)

        return validator

    @staticmethod
    def valid_calc_int_expression(
        var_name: str | None = None, suffix_decimals: dict[str, int] | None = None
    ) -> Callable[[str], str]:
        def validator(v: str) -> str:
            var = VarInt(name=var_name, value=123) if var_name else None
            calc_int_expression(v, var=var, suffix_decimals=suffix_decimals)
            return v

        return validator

    @staticmethod
    def valid_calc_decimal_value() -> Callable[[str], str]:
        def validator(v: str) -> str:
            calc_decimal_value(v)
            return v

        return validator


def _read_lines_from_file(path: str) -> list[str]:
    try:
        lines = Path(path).expanduser().read_text().strip().splitlines()
        return [line.strip() for line in lines if line.strip()]
    except Exception as e:
        raise ValueError from e
