import re
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Optional, List
from ..auth import get_current_user
from ..db.session import get_session
from ..models import (
    User,
    EntryMedia as EntryMediaModel,
    EntryProp as EntryPropModel,
    Entry as EntryModel,
    EntryTag as EntryTagModel,
    Hobby as HobbyModel,
)
from ..schemas import PaginatedResponse, EntryListItem, SearchRequest
from ..services.uploads import public_url

router = APIRouter(prefix="/search", tags=["search"])


def sanitize_fts_query(query: str) -> str:
    """
    Sanitize FTS query to prevent injection and ensure valid FTS5 syntax.
    Keeps only ASCII word characters, quotes, asterisks, and spaces.
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )
    
    # Remove potentially dangerous characters, keep only safe FTS5 characters
    sanitized = re.sub(r'[^\w\s"*-]', ' ', query, flags=re.ASCII)
    
    # Clean up multiple spaces and strip
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    if not sanitized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query contains no valid characters"
        )
    
    # Limit query length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized


@router.get("/", response_model=PaginatedResponse[EntryListItem])
def search_entries(
    q: str = Query(..., description="Search query"),
    hobby_id: Optional[int] = Query(None),
    include_descendants: bool = Query(True),
    type_key: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Search entries using full-text search with optional filters"""
    
    # Sanitize the search query
    sanitized_query = sanitize_fts_query(q)
    
    # Build the base FTS ID query with BM25 rank
    base_query = (
        "SELECT e.id AS id FROM entry AS e "
        "JOIN entry_fts ON entry_fts.rowid = e.id "
        "WHERE entry_fts MATCH :query"
    )
    base_count = (
        "SELECT COUNT(*) FROM entry AS e "
        "JOIN entry_fts ON entry_fts.rowid = e.id "
        "WHERE entry_fts MATCH :query"
    )

    params = {"query": sanitized_query}

    # Add filters
    if hobby_id:
        if include_descendants:
            ids: List[int] = [hobby_id]
            queue = [hobby_id]
            while queue:
                hid = queue.pop(0)
                for (cid,) in session.query(HobbyModel.id).filter(HobbyModel.parent_id == hid).all():
                    ids.append(cid)
                    queue.append(cid)
            if ids:
                base_query += f" AND e.hobby_id IN ({','.join(str(i) for i in ids)})"
                base_count += f" AND e.hobby_id IN ({','.join(str(i) for i in ids)})"
        else:
            base_query += " AND e.hobby_id = :hobby_id"
            base_count += " AND e.hobby_id = :hobby_id"
            params["hobby_id"] = hobby_id

    if type_key:
        base_query += " AND e.type_key = :type_key"
        base_count += " AND e.type_key = :type_key"
        params["type_key"] = type_key

    if tag:
        base_query += (
            " AND EXISTS (SELECT 1 FROM entrytag et WHERE et.entry_id = e.id AND et.tag = :tag)"
        )
        base_count += (
            " AND EXISTS (SELECT 1 FROM entrytag et WHERE et.entry_id = e.id AND et.tag = :tag)"
        )
        params["tag"] = tag.lower()

    # Add ordering and pagination
    search_query = base_query + " ORDER BY bm25(entry_fts), e.created_at DESC LIMIT :limit OFFSET :offset"
    params.update({"limit": limit, "offset": offset})

    # Execute queries
    id_rows = session.execute(text(search_query), params).fetchall()
    total = int(session.execute(text(base_count), params).scalar() or 0)

    ids = [row[0] for row in id_rows]
    items: list[EntryListItem] = []
    if ids:
        entries = session.query(EntryModel).filter(EntryModel.id.in_(ids)).all()
        by_id = {e.id: e for e in entries}
        ordered = [by_id[i] for i in ids if i in by_id]
    else:
        ordered = []
        
        # Get media count and thumbnail
        media_count = session.query(func.count(EntryMediaModel.id)).filter(
            EntryMediaModel.entry_id == entry.id
        ).scalar() or 0
        
        thumbnail = session.query(EntryMediaModel).filter(
            EntryMediaModel.entry_id == entry.id,
            EntryMediaModel.kind == 'image'
        ).first()
        
        # Get props as dict
        props = {}
        entry_props = session.query(EntryPropModel).filter(
            EntryPropModel.entry_id == entry.id
        ).all()
        for prop in entry_props:
            props[prop.key] = prop.value_text
        
        item = EntryListItem(
            id=entry.id,
            hobby_id=entry.hobby_id,
            type_key=entry.type_key,
            title=entry.title,
            description=entry.description,
            tags=entry.tags,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            media_count=media_count,
            thumbnail_url=public_url(thumbnail.file_path) if thumbnail else None,
            props=props
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )
