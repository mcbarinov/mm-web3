import logging
import sys
from pathlib import Path

from loguru import logger
from rich.logging import RichHandler


def init_logger_old(debug: bool, debug_file: Path | None, info_file: Path | None) -> None:
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


class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base_message = super().format(record)
        # Стандартные атрибуты LogRecord
        standard_keys = set(vars(logging.makeLogRecord({})).keys())
        extras = [
            f"{k}={v}" for k, v in record.__dict__.items()
            if k not in standard_keys and not k.startswith("_")
        ]
        if extras:
            return f"{base_message} | {', '.join(extras)}"
        return base_message

def init_logger(debug: bool, debug_file: Path | None, info_file: Path | None) -> None:
    level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logging.root.handlers.clear()
    logging.root.setLevel(level)

    # Rich handler for console output
    console_handler = RichHandler(
        level=level,
        rich_tracebacks=True,
        markup=True,
        show_level=debug,
        show_time=debug,
        show_path=debug,
    )
    console_formatter = ExtraFormatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    logging.root.addHandler(console_handler)

    # Optional debug file
    if debug_file:
        debug_file_handler = logging.FileHandler(debug_file.expanduser(), mode="a", encoding="utf-8")
        debug_file_handler.setLevel(logging.DEBUG)
        debug_formatter = ExtraFormatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
        debug_file_handler.setFormatter(debug_formatter)
        logging.root.addHandler(debug_file_handler)

    # Optional info file
    if info_file:
        info_file_handler = logging.FileHandler(info_file.expanduser(), mode="a", encoding="utf-8")
        info_file_handler.setLevel(logging.INFO)
        info_formatter = ExtraFormatter("%(message)s")
        info_file_handler.setFormatter(info_formatter)
        logging.root.addHandler(info_file_handler)


def get_log_prefix(log_prefix: str | None) -> str:
    prefix = log_prefix or ""
    if prefix:
        prefix += ": "
    return prefix
