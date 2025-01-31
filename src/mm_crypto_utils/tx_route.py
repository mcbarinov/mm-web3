from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import mm_std
from pydantic import BaseModel

from mm_crypto_utils.account import read_items_from_file


class TxRoute(BaseModel):
    from_address: str
    to_address: str

    @staticmethod
    def from_str(value: str | None, is_address_valid: Callable[[str], bool], to_lower: bool = False) -> list[TxRoute]:
        result: list[TxRoute] = []
        if value is None:
            return result
        if to_lower:
            value = value.lower()
        for line in mm_std.str_to_list(value, remove_comments=True):
            arr = line.split()
            if len(arr) == 2:
                from_address = arr[0]
                to_address = arr[1]
                if is_address_valid(from_address) and is_address_valid(to_address):
                    result.append(TxRoute(from_address=from_address, to_address=to_address))
                else:
                    raise ValueError(f"illegal line in addresses_map: {line}")
            else:
                raise ValueError(f"illegal line in addresses_map: {line}")

        return result

    @staticmethod
    def from_files(
        addresses_from_file: Path,
        addresses_to_file: Path,
        is_address: Callable[[str], bool],
        to_lower: bool = False,
    ) -> list[TxRoute]:
        addresses_from_file = addresses_from_file.expanduser()
        addresses_to_file = addresses_to_file.expanduser()

        if not addresses_from_file.is_file():
            raise ValueError(f"addresses_from_file={addresses_from_file} is not a file")

        if not addresses_to_file.is_file():
            raise ValueError(f"addresses_to_file={addresses_to_file} is not a file")

        addresses_from = read_items_from_file(addresses_from_file, is_address, to_lower)
        addresses_to = read_items_from_file(addresses_to_file, is_address, to_lower)
        if len(addresses_from) != len(addresses_to):
            raise ValueError("len(addresses_from) != len(addresses_to)")

        return [
            TxRoute(from_address=from_address, to_address=to_address)
            for from_address, to_address in zip(addresses_from, addresses_to, strict=True)
        ]
