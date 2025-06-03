import random
from collections.abc import Sequence


def random_str_choice(source: Sequence[str] | str | None) -> str | None:
    """
    Returns a random string from the given source.

    Args:
        source: A sequence of strings, a single string, or None

    Returns:
        - None if source is None
        - The original string if source is a string
        - Random string from sequence if source is a non-empty sequence
        - None if source is an empty sequence
    """
    if source is None:
        return None

    if isinstance(source, str):
        return source

    # source is a Sequence[str] at this point
    if source:
        return random.choice(source)

    return None
