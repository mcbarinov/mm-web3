import os
from pathlib import Path


def read_lines_from_file(source: Path | str, to_lower: bool = False) -> list[str]:
    if isinstance(source, str):
        source = Path(source)
    source = source.expanduser()
    if not source.is_file() or not os.access(source, os.R_OK):
        raise ValueError(f"Can't read file: {source}")
    try:
        data = source.expanduser().read_text().strip()
        if to_lower:
            data = data.lower()
        return [line.strip() for line in data.splitlines() if line.strip()]
    except Exception as e:
        raise ValueError from e
