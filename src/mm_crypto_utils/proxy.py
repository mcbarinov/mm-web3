from collections.abc import Sequence

from mm_std import random_str_choice

type Proxies = str | Sequence[str] | None


def random_proxy(proxies: Proxies) -> str | None:
    return random_str_choice(proxies)
