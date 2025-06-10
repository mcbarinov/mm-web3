from collections.abc import Callable
from pathlib import Path


def read_items_from_file(path: Path, is_valid: Callable[[str], bool], lowercase: bool = False) -> list[str]:
    """Read items from a file and validate them.

    Raises:
        ValueError: if the file cannot be read or any item is invalid.
    """
    path = path.expanduser()
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

    try:
        with path.open() as file:
            items = []
            for line_num, line in enumerate(file, 1):
                item = line.strip()
                if not item:  # Skip empty lines
                    continue

                if lowercase:
                    item = item.lower()

                if not is_valid(item):
                    raise ValueError(f"Invalid item in {path} at line {line_num}: {item}")
                items.append(item)

            return items
    except OSError as e:
        raise ValueError(f"Cannot read file {path}: {e}") from e
