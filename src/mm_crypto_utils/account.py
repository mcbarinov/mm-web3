from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from pathlib import Path

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


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

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: type, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.dict_schema(keys_schema=core_schema.str_schema(), values_schema=core_schema.str_schema(), strict=True)

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
