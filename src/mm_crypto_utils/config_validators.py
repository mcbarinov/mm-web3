import os
from collections.abc import Callable
from pathlib import Path

import pydash
from mm_std import str_to_list

from mm_crypto_utils.account import AddressToPrivate
from mm_crypto_utils.tx_route import TxRoute

type IsAddress = Callable[[str], bool]


class ConfigValidators:
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
    def address(is_address: IsAddress, lower: bool = False) -> Callable[[str], str]:
        def validator(v: str) -> str:
            if not is_address(v):
                raise ValueError(f"illegal address: {v}")
            if lower:
                return v.lower()
            return v

        return validator

    @staticmethod
    def addresses(
        unique: bool, lower: bool = False, is_address: IsAddress | None = None
    ) -> Callable[[str | list[str] | None], list[str]]:
        def validator(v: str | list[str] | None) -> list[str]:
            if v is None:
                return []
            if isinstance(v, str):
                addresses = str_to_list(v, unique=True, remove_comments=True, split_line=True, lower=lower)
            else:
                addresses = [address.lower() if lower else address for address in v]

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
    def routes(is_address: IsAddress) -> Callable[[str | None], list[TxRoute]]:
        def validator(v: str | None) -> list[TxRoute]:
            return TxRoute.from_str(v, is_address) if v else []

        return validator
