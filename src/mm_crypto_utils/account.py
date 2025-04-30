from __future__ import annotations

import contextlib
import os
from collections.abc import Callable
from pathlib import Path

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo


def read_items_from_file(source: Path, is_valid: Callable[[str], bool], to_lower: bool = False) -> list[str]:
    """Read items (addresses, private keys, etc.) from a file and validate them.
    Raises:
        ValueError: if the file cannot be read or any item is invalid.

    """
    source = source.expanduser()
    if not source.is_file():  # TODO: check can  read from this file
        raise ValueError(f"{source} is not a file")

    items = []
    data = source.read_text().strip()
    if to_lower:
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
    def __get_pydantic_core_schema__(cls, _source: object, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        # Use the dict schema as the basis.
        return core_schema.with_info_after_validator_function(
            cls.validate,  # our function that converts a dict to AddressToPrivate
            handler(dict),  # get the schema for a plain dict
        )

    @classmethod
    def validate(cls, value: object, _info: ValidationInfo) -> AddressToPrivate:
        """
        Convert and validate an input value into an AddressToPrivate.

        - If the input is already an AddressToPrivate, return it.
        - If it is a dict, check that all keys and values are strings and
          then return an AddressToPrivate.
        - Otherwise, raise a TypeError.
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            # Optionally, ensure all keys and values are strings.
            if not all(isinstance(k, str) for k in value):
                raise TypeError("All keys in AddressToPrivate must be strings")
            if not all(isinstance(v, str) for v in value.values()):
                raise TypeError("All values in AddressToPrivate must be strings")
            return cls(value)
        raise TypeError("Invalid type for AddressToPrivate. Expected dict or AddressToPrivate.")

    @staticmethod
    def from_list(private_keys: list[str], address_from_private: Callable[[str], str]) -> AddressToPrivate:
        """Create a dictionary of private keys with addresses as keys.
        Raises:
            ValueError: if private key is invalid
        """
        result = AddressToPrivate()
        for private_key in private_keys:
            address = None
            with contextlib.suppress(Exception):
                address = address_from_private(private_key)
            if address is None:
                raise ValueError("invalid private key")
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
