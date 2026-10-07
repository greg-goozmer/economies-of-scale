from functools import lru_cache


@lru_cache(maxsize=1)
def current_user_id() -> int:
    """LR3 singleton: a fixed creator until authentication is added in LR4."""
    return 101
