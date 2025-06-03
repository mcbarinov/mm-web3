from collections.abc import Sequence

from .utils import random_str_choice

type Nodes = str | Sequence[str]
"""
Type alias for JSON RPC node configuration.

Can be either:
- A single node URL as string
- A sequence (list, tuple) of node URLs
"""


def random_node(nodes: Nodes, remove_slash: bool = True) -> str:
    """
    Select a random JSON RPC node from the provided nodes.

    Args:
        nodes: Single node URL or sequence of node URLs
        remove_slash: Whether to remove trailing slash from the URL

    Returns:
        Selected node URL

    Raises:
        ValueError: When no valid node can be selected
    """
    selected = random_str_choice(nodes)
    if selected is None:
        raise ValueError("No valid node available for selection")

    if remove_slash and selected.endswith("/"):
        selected = selected.removesuffix("/")

    return selected
