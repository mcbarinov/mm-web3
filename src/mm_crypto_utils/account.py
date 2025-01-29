from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from pathlib import Path

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


def read_items_from_file(source: Path, is_valid: Callable[[str], bool], lowercase: bool = False) -> list[str]:
    """Read items (addresses, private keys, etc.) from a file and validate them.
    Raises:
        ValueError: if the file cannot be read or any item is invalid.

    """
    source = source.expanduser()
    if not source.is_file():  # TODO: check can  read from this file
        raise ValueError(f"{source} is not a file")

    items = []
    data = source.read_text().strip()
    if lowercase:
        data = data.lower()

    for line in data.split("\n"):
        if not is_valid(line):
            raise ValueError(f"illegal address in {source}: {line}")
        items.append(line)

    return items


class AddressToPrivate(dict[str, str]):
    """Map of addresses to private keys."""

    def contains_all_addresses(self, addresses: list[str]) -> bool:
        """Check if all addresses are in the map."""
        return set(addresses) <= set(self.keys())

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: type, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.dict_schema(keys_schema=core_schema.str_schema(), values_schema=core_schema.str_schema(), strict=True)

    @staticmethod
    def from_list(private_keys: list[str], address_from_private: Callable[[str], str]) -> AddressToPrivate:
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
            result[address] = private_key
        return result

    @staticmethod
    def from_file(private_keys_file: Path, address_from_private: Callable[[str], str]) -> AddressToPrivate:
        """Create a dictionary of private keys with addresses as keys from a file.
        Raises:
            ValueError: If the file cannot be read or any private key is invalid.
        """
        private_keys_file = private_keys_file.expanduser()
        if not os.access(private_keys_file, os.R_OK):
            raise ValueError(f"can't read from the file: {private_keys_file}")

        private_keys = private_keys_file.read_text().strip().split("\n")
        return AddressToPrivate.from_list(private_keys, address_from_private)
