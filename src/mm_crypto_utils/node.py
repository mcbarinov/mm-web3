from collections.abc import Sequence
from typing import cast

from mm_std import random_choice

type Nodes = str | Sequence[str]


def random_node(nodes: Nodes, remove_slash: bool = True) -> str:
    node = cast(str, random_choice(nodes))
    if remove_slash and node.endswith("/"):
        node = node.removesuffix("/")
    return node
