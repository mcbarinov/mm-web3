import pytest

from mm_crypto_utils import proxy
from mm_crypto_utils.proxy import is_valid_proxy_url

pytestmark = pytest.mark.asyncio


def test_valid_proxy_urls():
    valid_urls = [
        "socks5h://user:pass@proxy.example.com:1080",
        "http://proxy.example.com:8080",
        "socks4://proxy.example.com:1080",
        "socks5://proxy.example.com:1080",
    ]
    for url in valid_urls:
        assert is_valid_proxy_url(url), f"URL should be valid: {url}"


def test_invalid_proxy_urls():
    invalid_urls = [
        "socks4://user:pass@proxy.example.com:1080",  # SOCKS4 with authentication
        "ftp://proxy.example.com:21",  # Unsupported scheme
        "http://proxy.example.com",  # Missing port
        "socks4://proxy.example.com:1080/bla-bla-bla",  # Extra path component
        "socks5://proxy.example.com",  # Missing port
        "://proxy.example.com:1080",  # Missing scheme
    ]
    for url in invalid_urls:
        assert not is_valid_proxy_url(url), f"URL should be invalid: {url}"


async def test_fetch_proxies(proxies_url):
    res = await proxy.fetch_proxies(proxies_url, timeout=5)
    assert res.is_ok()
    assert len(res.unwrap()) > 10


async def test_fetch_proxies_sync(proxies_url):
    res = proxy.fetch_proxies_sync(proxies_url, timeout=5)
    assert res.is_ok()
    assert len(res.unwrap()) > 10
