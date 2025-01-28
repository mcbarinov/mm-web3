import sys
from typing import NoReturn

from mm_std import BaseConfig, print_json


def print_config_and_exit(config: BaseConfig, exclude: set[str] | None = None) -> NoReturn:
    print_json(config.model_dump(exclude=exclude))
    sys.exit(0)
