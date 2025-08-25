from __future__ import annotations

from collections.abc import Iterable


def normalize_tags(tags: str | Iterable[str] | None) -> list[str]:
    """Normalize tags to a lowercase, trimmed unique list.

    Accepts CSV string or iterable of strings.
    """
    if tags is None:
        return []
    items: Iterable[str]
    if isinstance(tags, str):
        # Split on commas
        items = [t for t in (s.strip() for s in tags.split(",")) if t]
    else:
        items = (str(t).strip() for t in tags)
    norm = []
    seen = set()
    for t in items:
        if not t:
            continue
        v = t.lower()
        if v not in seen:
            seen.add(v)
            norm.append(v)
    return norm


def join_tags(tags: Iterable[str]) -> str:
    return ", ".join(tags)

