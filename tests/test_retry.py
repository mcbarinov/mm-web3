from mm_std import Result

from mm_crypto import retry_with_node_and_proxy, retry_with_proxy


async def test_retry_with_node_and_proxy_success_on_first_try():
    async def fake_func(node: str, proxy: str | None) -> Result[str]:
        return Result.ok(f"{node}_{proxy}")

    result = await retry_with_node_and_proxy(
        retries=3, nodes=["node1", "node2"], proxies=["proxy1", "proxy2"], func=lambda node, proxy: fake_func(node, proxy)
    )

    assert result.is_ok()
    assert "retry_logs" in result.extra
    assert len(result.extra["retry_logs"]) == 1


async def test_retry_with_node_and_proxy_success_on_retry():
    attempts = []

    async def flaky_func(node: str, proxy: str | None) -> Result[str]:
        attempts.append((node, proxy))
        if len(attempts) < 2:
            return Result.err("temporary_error")
        return Result.ok("finally")

    result = await retry_with_node_and_proxy(
        retries=3, nodes=["n1"], proxies=["p1"], func=lambda node, proxy: flaky_func(node, proxy)
    )

    assert result.is_ok()
    assert result.unwrap() == "finally"
    assert len(result.extra["retry_logs"]) == 2


async def test_retry_with_node_and_proxy_all_failures():
    async def always_fail(_node: str, _proxy: str | None) -> Result[str]:
        return Result.err("fail")

    result = await retry_with_node_and_proxy(
        retries=3, nodes=["n1"], proxies=["p1"], func=lambda node, proxy: always_fail(node, proxy)
    )

    assert result.is_err()
    assert result.unwrap_error() == "fail"
    assert len(result.extra["retry_logs"]) == 3


async def test_retry_with_proxy_success():
    async def success_on_second_try(_proxy: str | None) -> Result[str]:
        success_on_second_try.counter += 1
        if success_on_second_try.counter < 2:
            return Result.err("fail")
        return Result.ok("ok")

    success_on_second_try.counter = 0

    result = await retry_with_proxy(retries=3, proxies=["proxy1", "proxy2"], func=lambda proxy: success_on_second_try(proxy))

    assert result.is_ok()
    assert result.unwrap() == "ok"
    assert len(result.extra["retry_logs"]) == 2


async def test_retry_with_proxy_failure():
    async def always_fail(_proxy: str | None) -> Result[str]:
        return Result.err("proxy_error")

    result = await retry_with_proxy(retries=2, proxies=["p1", "p2"], func=lambda proxy: always_fail(proxy))

    assert result.is_err()
    assert result.unwrap_error() == "proxy_error"
    assert len(result.extra["retry_logs"]) == 2
