from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from ..auth import get_current_user
from ..db import get_session
from ..models import User
from ..schemas import PaginatedResponse, EntryListItem, SearchRequest

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=PaginatedResponse[EntryListItem])
def search_entries(
    q: str = Query(..., description="Search query"),
    hobby_id: Optional[int] = Query(None),
    type_key: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Search entries using full-text search with optional filters"""
    
    # Build the base FTS query
    base_query = """
        SELECT e.*, rank
        FROM entry e
        JOIN entry_fts ON entry_fts.rowid = e.id
        WHERE entry_fts MATCH :query
    """
    
    base_count = """
        SELECT COUNT(*)
        FROM entry e
        JOIN entry_fts ON entry_fts.rowid = e.id
        WHERE entry_fts MATCH :query
    """
    
    params = {"query": q}
    
    # Add filters
    filters = []
    if hobby_id:
        filters.append("e.hobby_id = :hobby_id")
        params["hobby_id"] = hobby_id
    
    if type_key:
        filters.append("e.type_key = :type_key")
        params["type_key"] = type_key
    
    if tag:
        filters.append("e.tags LIKE :tag")
        params["tag"] = f"%{tag}%"
    
    if filters:
        filter_clause = " AND " + " AND ".join(filters)
        base_query += filter_clause
        base_count += filter_clause
    
    # Add ordering and pagination
    search_query = base_query + " ORDER BY rank, e.created_at DESC LIMIT :limit OFFSET :offset"
    params.update({"limit": limit, "offset": offset})
    
    # Execute queries
    results = session.execute(text(search_query), params).fetchall()
    total = session.execute(text(base_count), params).scalar()
    
    # Convert results to EntryListItem format
    items = []
    for result in results:
        entry = result[0]  # First element is the entry object
        rank = result[1]   # Second element is the FTS rank
        
        item = EntryListItem(
            id=entry.id,
            hobby_id=entry.hobby_id,
            type_key=entry.type_key,
            title=entry.title,
            description=entry.description,
            tags=entry.tags,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            media_count=0,  # TODO: Calculate media count if needed
            thumbnail_url=None,  # TODO: Get thumbnail if needed
            props={}  # TODO: Get props if needed
        )
        items.append(item)
    
    return PaginatedResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total
    )