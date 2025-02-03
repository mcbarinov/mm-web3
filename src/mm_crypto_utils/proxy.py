from collections.abc import Sequence

import pydash
from mm_std import Err, Ok, Result, fatal, hr, random_str_choice

type Proxies = str | Sequence[str] | None


def random_proxy(proxies: Proxies) -> str | None:
    return random_str_choice(proxies)


def fetch_proxies_or_fatal(proxies_url: str, timeout: float = 10) -> list[str]:
    """Fetch proxies from the given url. If it can't fetch, exit with error."""
    try:
        res = hr(proxies_url, timeout=timeout)
        if res.is_error():
            fatal(f"Can't get proxies: {res.error}")
        proxies = [p.strip() for p in res.body.splitlines() if p.strip()]
        return pydash.uniq(proxies)
    except Exception as err:
        fatal(f"Can't get  proxies from the url: {err}")


def fetch_proxies(proxies_url: str) -> Result[list[str]]:
    """Fetch proxies from the given url. If it can't fetch, return error."""
    try:
        res = hr(proxies_url, timeout=10)
        if res.is_error():
            return Err(f"Can't get proxies: {res.error}")
        proxies = [p.strip() for p in res.body.splitlines() if p.strip()]
        return Ok(pydash.uniq(proxies))
    except Exception as err:
        return Err(f"Can't get  proxies from the url: {err}")
