from collections.abc import Sequence
from urllib.parse import urlparse

import pydash
from mm_std import Result, fatal, http_request, http_request_sync, random_str_choice

type Proxies = str | Sequence[str] | None


def random_proxy(proxies: Proxies) -> str | None:
    return random_str_choice(proxies)


async def fetch_proxies_or_fatal(proxies_url: str, timeout: float = 5) -> list[str]:
    """Fetch proxies from the given url. If it can't fetch, exit with error."""
    res = await fetch_proxies(proxies_url, timeout=timeout)
    if res.is_err():
        fatal(f"Can't get proxies: {res.error}")
    return res.unwrap()


async def fetch_proxies(proxies_url: str, timeout: float = 5) -> Result[list[str]]:
    """Fetch proxies from the given url. Response is a list of proxies, one per line. Each proxy must be valid."""
    res = await http_request(proxies_url, timeout=timeout)
    if res.is_err():
        return res.to_err()

    proxies = [p.strip() for p in (res.body or "").splitlines() if p.strip()]
    proxies = pydash.uniq(proxies)
    for proxy in proxies:
        if not is_valid_proxy_url(proxy):
            return res.to_err(f"Invalid proxy URL: {proxy}")

    if not proxies:
        return res.to_err("No valid proxies found")
    return res.to_ok(proxies)


def fetch_proxies_sync(proxies_url: str, timeout: float = 5) -> Result[list[str]]:
    res = http_request_sync(proxies_url, timeout=timeout)
    if res.is_err():
        return res.to_err()

    proxies = [p.strip() for p in (res.body or "").splitlines() if p.strip()]
    proxies = pydash.uniq(proxies)
    for proxy in proxies:
        if not is_valid_proxy_url(proxy):
            return res.to_err(f"Invalid proxy URL: {proxy}")

    if not proxies:
        return res.to_err("No valid proxies found")
    return res.to_ok(proxies)


def fetch_proxies_or_fatal_sync(proxies_url: str, timeout: float = 5) -> list[str]:
    res = fetch_proxies_sync(proxies_url, timeout=timeout)
    if res.is_err():
        fatal(f"Can't get proxies: {res.error}")
    return res.unwrap()


def is_valid_proxy_url(proxy_url: str) -> bool:
    """
    Check if the given URL is a valid proxy URL.

    A valid proxy URL must have:
      - A scheme in {"http", "https", "socks4", "socks5", "zsocks5h"}.
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
