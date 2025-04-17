from collections.abc import Awaitable, Callable

from mm_std import Result

from mm_crypto_utils.node import Nodes, random_node
from mm_crypto_utils.proxy import Proxies, random_proxy


async def retry_node_call[T](
    retries: int, nodes: Nodes, proxies: Proxies, func: Callable[..., Awaitable[Result[T]]], **kwargs: object
) -> Result[T]:
    res: Result[T] = Result.failure("not_started")
    logs = []
    for _ in range(retries):
        node = random_node(nodes)
        proxy = random_proxy(proxies)
        res = await func(node, proxy=proxy, **kwargs)
        logs.append({"node": node, "proxy": proxy, "result": res.to_dict()})
        if res.is_ok():
            return Result.success(res.unwrap(), extra={"retry_logs": logs})
    return Result.failure(res.unwrap_error(), extra={"retry_logs": logs})
