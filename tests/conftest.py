import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="session")
def proxies_url() -> str:
    proxies_url = os.getenv("PROXIES_URL")
    if not proxies_url:
        raise ValueError("PROXIES_URL environment variable is not set")
    return proxies_url
