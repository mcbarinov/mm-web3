import sys
from pathlib import Path

from loguru import logger


def init_loguru(debug: bool, debug_file: Path | None, info_file: Path | None) -> None:
    """Initialize loguru logger with console and optional file outputs.

    Args:
        debug: If True, set DEBUG level with timestamps; otherwise INFO level with plain format
        debug_file: Optional file path for DEBUG level logs with timestamps
        info_file: Optional file path for INFO level logs with plain format
    """
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
