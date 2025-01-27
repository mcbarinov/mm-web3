import sys
from pathlib import Path

from loguru import logger


def init_logger(debug: bool, debug_file: Path | None, info_file: Path | None) -> None:
    if debug:
        level = "DEBUG"
        format_ = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <level>{level}</level> {message}"
    else:
        level = "INFO"
        format_ = "{message}"

    logger.remove()
    logger.add(sys.stderr, format=format_, colorize=True, level=level)
    if debug_file:
        logger.add(debug_file.expanduser(), format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}")
    if info_file:
        logger.add(info_file.expanduser(), format="{message}", level="INFO")


def get_log_prefix(log_prefix: str | None) -> str:
    prefix = log_prefix or ""
    if prefix:
        prefix += ": "
    return prefix
