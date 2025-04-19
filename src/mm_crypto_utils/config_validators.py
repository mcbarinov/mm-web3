import os
from collections.abc import Callable
from pathlib import Path

import pydash
from mm_std import str_to_list
from pydantic import BaseModel

from mm_crypto_utils import calc_decimal_value, calc_int_expression
from mm_crypto_utils.account import AddressToPrivate
from mm_crypto_utils.calcs import VarInt
from mm_crypto_utils.proxy import fetch_proxies_sync
from mm_crypto_utils.utils import read_lines_from_file

type IsAddress = Callable[[str], bool]


class Transfer(BaseModel):
    from_address: str
    to_address: str
    value: str  # can be empty string

    @property
    def log_prefix(self) -> str:
        return f"{self.from_address}->{self.to_address}"


class ConfigValidators:
    @staticmethod
    def transfers(is_address: IsAddress, to_lower: bool = False) -> Callable[[str], list[Transfer]]:
        def validator(v: str) -> list[Transfer]:
            result = []
            for line in str_to_list(v, remove_comments=True):  # don't use to_lower here because it can be a file: /To/Path.txt
                if line.startswith("file:"):
                    for file_line in read_lines_from_file(line.removeprefix("file:").strip()):
                        arr = file_line.split()
                        if len(arr) < 2 or len(arr) > 3:
                            raise ValueError(f"illegal file_line: {file_line}")
                        result.append(Transfer(from_address=arr[0], to_address=arr[1], value=arr[2] if len(arr) > 2 else ""))

                else:
                    arr = line.split()
                    if len(arr) < 2 or len(arr) > 3:
                        raise ValueError(f"illegal line: {line}")
                    result.append(Transfer(from_address=arr[0], to_address=arr[1], value=arr[2] if len(arr) > 2 else ""))

            if to_lower:
                result = [
                    Transfer(from_address=r.from_address.lower(), to_address=r.to_address.lower(), value=r.value) for r in result
                ]

            for route in result:
                if not is_address(route.from_address):
                    raise ValueError(f"illegal address: {route.from_address}")
                if not is_address(route.to_address):
                    raise ValueError(f"illegal address: {route.to_address}")

            if not result:
                raise ValueError("empty")

            return result

        return validator

    @staticmethod
    def proxies() -> Callable[[str], list[str]]:
        def validator(v: str) -> list[str]:
            result = []
            for line in str_to_list(v, unique=True, remove_comments=True):
                if line.startswith("url:"):
                    url = line.removeprefix("url:").strip()
                    res = fetch_proxies_sync(url)
                    if res.is_err():
                        raise ValueError(f"Can't get proxies: {res.unwrap_error()}")
                    result += res.unwrap()
                elif line.startswith("env_url:"):
                    env_var = line.removeprefix("env_url:").strip()
                    url = os.getenv(env_var) or ""
                    if not url:
                        raise ValueError(f"missing env var: {env_var}")
                    res = fetch_proxies_sync(url)
                    if res.is_err():
                        raise ValueError(f"Can't get proxies: {res.unwrap_error()}")
                    result += res.unwrap()
                elif line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    result += read_lines_from_file(path)
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
    def nodes(allow_empty: bool = False) -> Callable[[str], list[str]]:
        def validator(v: str) -> list[str]:
            nodes = str_to_list(v, unique=True, remove_comments=True)
            if not allow_empty and not nodes:
                raise ValueError("empty nodes")
            return nodes

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
            result = []
            for line in str_to_list(v, unique=unique, remove_comments=True):
                if line.startswith("file:"):  # don't use to_lower here because it can be a file: /To/Path.txt
                    path = line.removeprefix("file:").strip()
                    result += read_lines_from_file(path, to_lower=to_lower)
                else:
                    result.append(line)
            result = pydash.uniq(result)

            if to_lower:
                result = [r.lower() for r in result]

            if is_address:
                for address in result:
                    if not is_address(address):
                        raise ValueError(f"illegal address: {address}")
            return result

        return validator

    @staticmethod
    def private_keys(address_from_private: Callable[[str], str]) -> Callable[[str], AddressToPrivate]:
        def validator(v: str) -> AddressToPrivate:
            private_keys = []
            for line in str_to_list(v, unique=True, remove_comments=True):
                if line.startswith("file:"):
                    path = line.removeprefix("file:").strip()
                    private_keys += read_lines_from_file(path)
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
