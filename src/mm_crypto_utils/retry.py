from collections.abc import Awaitable, Callable

from mm_std import DataResult

from mm_crypto_utils.node import Nodes, random_node
from mm_crypto_utils.proxy import Proxies, random_proxy


async def retry_node_call[T](
    retries: int, nodes: Nodes, proxies: Proxies, func: Callable[..., Awaitable[DataResult[T]]], **kwargs: object
) -> DataResult[T]:
    res: DataResult[T] = DataResult(err="not_started")
    logs = []
    for _ in range(retries):
        node = random_node(nodes)
        proxy = random_proxy(proxies)
        res = await func(node, proxy=proxy, **kwargs)
        logs.append({"node": node, "proxy": proxy, "result": res.dict()})
        if res.is_ok():
            return DataResult(ok=res.unwrap(), data={"retry_logs": logs}, ok_is_none=True)
    return DataResult(err=res.unwrap_err(), data={"retry_logs": logs})
