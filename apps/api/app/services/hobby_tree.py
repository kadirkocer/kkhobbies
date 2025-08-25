from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from ..models import Hobby


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s or "hobby"


def ensure_unique_slug(session: Session, base: str, exclude_id: int | None = None) -> str:
    slug = base
    n = 1
    while True:
        q = session.query(Hobby).filter(Hobby.slug == slug)
        if exclude_id is not None:
            q = q.filter(Hobby.id != exclude_id)
        if not session.query(q.exists()).scalar():
            return slug
        n += 1
        slug = f"{base}-{n}"


def get_hobby_tree(session: Session) -> list[dict[str, Any]]:
    hobbies = session.query(Hobby).order_by(Hobby.sort_order, Hobby.id).all()
    by_parent: dict[int | None, list[Hobby]] = {}
    for h in hobbies:
        by_parent.setdefault(h.parent_id, []).append(h)

    def node(h: Hobby) -> dict[str, Any]:
        return {
            "id": h.id,
            "name": h.name,
            "slug": h.slug,
            "color": h.color,
            "icon": h.icon,
            "sort_order": h.sort_order,
            "children": [node(ch) for ch in by_parent.get(h.id, [])],
        }

    roots = by_parent.get(None, [])
    # Sort children lists by sort_order
    for lst in by_parent.values():
        lst.sort(key=lambda x: (x.sort_order, x.id))
    return [node(r) for r in roots]

