import os
from pathlib import Path

from mm_std import str_to_list


class ConfigValidators:
    @staticmethod
    def log_file(v: Path | None) -> Path | None:
        if v is None:
            return None
        log_file = Path(v).expanduser()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        log_file.touch(exist_ok=True)
        if not log_file.is_file() or not os.access(log_file, os.W_OK):
            raise ValueError(f"wrong log path: {v}")
        return v

    @staticmethod
    def nodes(v: str | list[str] | None) -> list[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return str_to_list(v, unique=True, remove_comments=True, split_line=True)
        return v
