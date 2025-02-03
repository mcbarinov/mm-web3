import os
from collections.abc import Callable
from pathlib import Path

import pydash
from mm_std import Err, str_to_list

from mm_crypto_utils import calc_decimal_value, calc_int_expression
from mm_crypto_utils.account import AddressToPrivate
from mm_crypto_utils.calcs import VarInt
from mm_crypto_utils.proxy import fetch_proxies
from mm_crypto_utils.tx_route import TxRoute

type IsAddress = Callable[[str], bool]


class ConfigValidators:
    @staticmethod
    def proxies() -> Callable[[str | list[str] | None], list[str]]:
        def validator(v: str | list[str] | None) -> list[str]:
            if v is None or not v:
                return []
            result = []
            lines = str_to_list(v, unique=True, remove_comments=True) if isinstance(v, str) else v
            for line in lines:
                if line.startswith("url:"):
                    url = line.removeprefix("url:").strip()
                    res = fetch_proxies(url)
                    if isinstance(res, Err):
                        raise ValueError(f"Can't get proxies: {res.err}")
                    result += res.ok
                elif line.startswith("env_url:"):
                    env_var = line.removeprefix("env_url:").strip()
                    url = os.getenv(env_var)
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
    def log_file() -> Callable[[Path | None], Path | None]:
        def validator(v: Path | None) -> Path | None:
            if v is None:
                return None
            log_file = Path(v).expanduser()
            log_file.parent.mkdir(parents=True, exist_ok=True)
            log_file.touch(exist_ok=True)
            if not log_file.is_file() or not os.access(log_file, os.W_OK):
                raise ValueError(f"wrong log path: {v}")
            return v

        return validator

    @staticmethod
    def nodes() -> Callable[[str | list[str] | None], list[str]]:
        def validator(v: str | list[str] | None) -> list[str]:
            if v is None:
                return []
            if isinstance(v, str):
                return str_to_list(v, unique=True, remove_comments=True, split_line=True)
            return v

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
    def addresses(
        unique: bool, to_lower: bool = False, is_address: IsAddress | None = None
    ) -> Callable[[str | list[str] | None], list[str]]:
        def validator(v: str | list[str] | None) -> list[str]:
            if v is None:
                return []
            if isinstance(v, str):
                addresses = str_to_list(v, unique=True, remove_comments=True, split_line=True, lower=to_lower)
            else:
                addresses = [address.lower() if to_lower else address for address in v]

            if is_address:
                for address in addresses:
                    if not is_address(address):
                        raise ValueError(f"illegal address: {address}")

            if unique:
                return pydash.uniq(addresses)
            return addresses

        return validator

    @staticmethod
    def private_keys(address_from_private: Callable[[str], str]) -> Callable[[str | list[str] | None], AddressToPrivate]:
        def validator(v: str | list[str] | None) -> AddressToPrivate:
            if v is None:
                return AddressToPrivate()
            private_keys = str_to_list(v, unique=True, remove_comments=True) if isinstance(v, str) else v
            return AddressToPrivate.from_list(private_keys, address_from_private)

        return validator

    @staticmethod
    def routes(is_address: IsAddress, to_lower: bool = False) -> Callable[[str | None], list[TxRoute]]:
        def validator(v: str | None) -> list[TxRoute]:
            return TxRoute.from_str(v, is_address, to_lower=to_lower) if v else []

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
        return Path(path).expanduser().read_text().strip().splitlines()
    except Exception as e:
        raise ValueError from e
