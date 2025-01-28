from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from pathlib import Path

from mm_std import str_to_list
from pydantic import BaseModel


class TxRoute(BaseModel):
    from_address: str
    to_address: str

    @staticmethod
    def from_str(value: str | None, is_address_valid: Callable[[str], bool], lowercase: bool = False) -> list[TxRoute]:
        result: list[TxRoute] = []
        if value is None:
            return result
        if lowercase:
            value = value.lower()
        for line in str_to_list(value, remove_comments=True):
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
        is_address_valid: Callable[[str], bool],
        lowercase: bool = False,
    ) -> list[TxRoute]:
        addresses_from_file = addresses_from_file.expanduser()
        addresses_to_file = addresses_to_file.expanduser()

        if not addresses_from_file.is_file():
            raise ValueError(f"addresses_from_file={addresses_from_file} is not a file")

        if not addresses_to_file.is_file():
            raise ValueError(f"addresses_to_file={addresses_to_file} is not a file")

        addresses_from = read_addresses_from_file(addresses_from_file, is_address_valid, lowercase)
        addresses_to = read_addresses_from_file(addresses_to_file, is_address_valid, lowercase)
        if len(addresses_from) != len(addresses_to):
            raise ValueError("len(addresses_from) != len(addresses_to)")

        return [
            TxRoute(from_address=from_address, to_address=to_address)
            for from_address, to_address in zip(addresses_from, addresses_to, strict=False)
        ]


def read_addresses_from_file(source: Path, is_valid_address: Callable[[str], bool], lowercase: bool = False) -> list[str]:
    source = source.expanduser()
    if not source.is_file():
        raise ValueError(f"{source} is not a file")

    addresses = []
    data = source.read_text().strip()
    if lowercase:
        data = data.lower()

    for line in data.split("\n"):
        if not is_valid_address(line):
            raise ValueError(f"illegal address in {source}: {line}")
        addresses.append(line)

    return addresses


class AddressToPrivate(dict[str, str]):
    """Map of addresses to private keys."""

    @staticmethod
    def from_list(
        private_keys: list[str], address_from_private: Callable[[str], str | None], address_lowercase: bool = False
    ) -> AddressToPrivate:
        """Create a dictionary of private keys with addresses as keys.
        Raises:
            ValueError: if private key is invalid
        """
        result = AddressToPrivate()
        for private_key in private_keys:
            with contextlib.suppress(Exception):
                address = address_from_private(private_key)
            if address is None:
                raise ValueError(f"invalid private key: {private_key}")
            if address_lowercase:
                address = address.lower()
            result[address] = private_key
        return result

    @staticmethod
    def from_file(
        private_keys_file: Path, address_from_private: Callable[[str], str | None], address_lowercase: bool = False
    ) -> AddressToPrivate:
        """Create a dictionary of private keys with addresses as keys from a file.
        Raises:
            ValueError: If the file cannot be read or any private key is invalid.
        """
        private_keys_file = private_keys_file.expanduser()
        if not os.access(private_keys_file, os.R_OK):
            raise ValueError(f"can't read from the file: {private_keys_file}")

        private_keys = private_keys_file.read_text().strip().split("\n")
        return AddressToPrivate.from_list(private_keys, address_from_private, address_lowercase)
