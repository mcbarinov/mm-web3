from collections.abc import Sequence
from urllib.parse import urlparse

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
        proxies = pydash.uniq(proxies)
        for proxy in proxies:
            if not is_valid_proxy_url(proxy):
                return Err(f"Invalid proxy URL: {proxy} for the source: {proxies_url}")
        return Ok(proxies)
    except Exception as err:
        return Err(f"Can't get  proxies from the url: {err}")


def is_valid_proxy_url(proxy_url: str) -> bool:
    """
    Check if the given URL is a valid proxy URL.

    A valid proxy URL must have:
      - A scheme in {"http", "https", "socks4", "socks5", "socks5h"}.
      - A non-empty hostname.
      - A specified port.
      - No extra path components (the path must be empty or "/").

    For SOCKS4 URLs, authentication (username/password) is not supported.

    Examples:
      is_valid_proxy_url("socks5h://user:pass@proxy.example.com:1080") -> True
      is_valid_proxy_url("http://proxy.example.com:8080") -> True
      is_valid_proxy_url("socks4://proxy.example.com:1080") -> True
      is_valid_proxy_url("socks4://user:pass@proxy.example.com:1080") -> False
      is_valid_proxy_url("ftp://proxy.example.com:21") -> False
      is_valid_proxy_url("socks4://proxy.example.com:1080/bla-bla-bla") -> False
    """
    try:
        parsed = urlparse(proxy_url)
    except Exception:
        return False

    allowed_schemes = {"http", "https", "socks4", "socks5", "socks5h"}
    if parsed.scheme not in allowed_schemes:
        return False

    if not parsed.hostname:
        return False

    if not parsed.port:
        return False

    # For SOCKS4, authentication is not supported.
    if parsed.scheme == "socks4" and (parsed.username or parsed.password):
        return False

    # Ensure that there is no extra path (only allow an empty path or a single "/")
    if parsed.path and parsed.path not in ("", "/"):  # noqa: SIM103
        return False

    return True
