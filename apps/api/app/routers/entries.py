from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Literal
from ..auth import get_current_user
from ..db import get_session
from ..models import (
    User,
    Entry as EntryModel,
    EntryProp as EntryPropModel,
    EntryMedia as EntryMediaModel,
    EntryTag as EntryTagModel,
    Hobby as HobbyModel,
)
from ..schemas import (
    Entry, EntryCreate, EntryUpdate, EntryListItem,
    EntryProp, EntryPropBatch, EntryMedia, EntryMediaCreate,
    PaginatedResponse
)
from ..services.entry_validation import validate_entry_props
from ..services.uploads import store_upload, delete_upload, public_url
from ..services.tags import normalize_tags, join_tags

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("/", response_model=PaginatedResponse[EntryListItem])
def get_entries(
    q: Optional[str] = Query(None, description="Full-text search query"),
    hobby_id: Optional[int] = Query(None),
    type_key: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    include_descendants: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get entries with optional filters and search"""
    
    if q:
        # Full-text search using FTS5, order by BM25 rank (lower is better)
        id_query = text(
            """
            SELECT e.id AS id
            FROM entry AS e
            JOIN entry_fts ON entry_fts.rowid = e.id
            WHERE entry_fts MATCH :query
            ORDER BY bm25(entry_fts), e.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        )
        count_query = text(
            """
            SELECT COUNT(*)
            FROM entry AS e
            JOIN entry_fts ON entry_fts.rowid = e.id
            WHERE entry_fts MATCH :query
            """
        )
        params = {"query": q, "limit": limit, "offset": offset}
        id_rows = session.execute(id_query, params).fetchall()
        ids = [row[0] for row in id_rows]
        total = int(session.execute(count_query, {"query": q}).scalar() or 0)
        if ids:
            entries = (
                session.query(EntryModel)
                .filter(EntryModel.id.in_(ids))
                .all()
            )
            # Preserve order from FTS result
            by_id = {e.id: e for e in entries}
            entries = [by_id[i] for i in ids if i in by_id]
        else:
            entries = []
    else:
        # Regular query with filters
        query = session.query(EntryModel)
        
        if hobby_id:
            if include_descendants:
                ids = [hobby_id]
                queue = [hobby_id]
                while queue:
                    hid = queue.pop(0)
                    for (cid,) in session.query(HobbyModel.id).filter(HobbyModel.parent_id == hid).all():
                        ids.append(cid)
                        queue.append(cid)
                query = query.filter(EntryModel.hobby_id.in_(ids))
            else:
                query = query.filter(EntryModel.hobby_id == hobby_id)
        if type_key:
            query = query.filter(EntryModel.type_key == type_key)
        if tag:
            query = query.join(EntryTagModel, EntryTagModel.entry_id == EntryModel.id).filter(
                EntryTagModel.tag == tag.lower()
            )
        
        total = query.count()
        entries = query.order_by(EntryModel.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to EntryListItem format
    items = []
    for entry in entries:
        entry_obj = entry
            
        # Get media count and thumbnail
        media_count = session.query(func.count(EntryMediaModel.id)).filter(
            EntryMediaModel.entry_id == entry_obj.id
        ).scalar()
        
        thumbnail = session.query(EntryMediaModel).filter(
            EntryMediaModel.entry_id == entry_obj.id,
            EntryMediaModel.kind == 'image'
        ).first()
        
        # Get props as dict
        props = {}
        entry_props = session.query(EntryPropModel).filter(
            EntryPropModel.entry_id == entry_obj.id
        ).all()
        for prop in entry_props:
            props[prop.key] = prop.value_text
        
        item = EntryListItem(
            id=entry_obj.id,
            hobby_id=entry_obj.hobby_id,
            type_key=entry_obj.type_key,
            title=entry_obj.title,
            description=entry_obj.description,
            tags=entry_obj.tags,
            created_at=entry_obj.created_at,
            updated_at=entry_obj.updated_at,
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


@router.post("/", response_model=Entry)
def create_entry(
    entry_data: EntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new entry"""
    data = entry_data.model_dump()
    tag_list = normalize_tags(data.get("tags"))
    data["tags"] = join_tags(tag_list) if tag_list else None
    entry = EntryModel(**data)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    if tag_list:
        for t in tag_list:
            session.add(EntryTagModel(entry_id=entry.id, tag=t))
        session.commit()
    return entry


@router.get("/{entry_id}", response_model=Entry)
def get_entry(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    return entry


@router.patch("/{entry_id}", response_model=Entry)
def update_entry(
    entry_id: int,
    entry_update: EntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    update_data = entry_update.model_dump(exclude_unset=True)
    # Handle tags
    if "tags" in update_data:
        tag_list = normalize_tags(update_data.get("tags"))
        entry.tags = join_tags(tag_list) if tag_list else None
        session.query(EntryTagModel).filter(EntryTagModel.entry_id == entry.id).delete()
        for t in tag_list:
            session.add(EntryTagModel(entry_id=entry.id, tag=t))
        update_data.pop("tags", None)
    for field, value in update_data.items():
        setattr(entry, field, value)
    
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    session.delete(entry)
    session.commit()
    return {"message": "Entry deleted successfully"}


# Entry Properties endpoints
@router.get("/{entry_id}/props", response_model=List[EntryProp])
def get_entry_props(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get properties for an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    return session.query(EntryPropModel).filter(EntryPropModel.entry_id == entry_id).all()


@router.post("/{entry_id}/props", response_model=List[EntryProp])
def add_or_replace_entry_props(
    entry_id: int,
    props_data: EntryPropBatch,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Add or replace properties for an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    # Validate props against schema
    validation_result = validate_entry_props(session, entry.type_key, props_data.props)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Property validation failed: {'; '.join(validation_result['errors'])}"
        )
    
    # Remove existing props and add new ones
    session.query(EntryPropModel).filter(EntryPropModel.entry_id == entry_id).delete()
    
    new_props = []
    for prop_data in props_data.props:
        prop = EntryPropModel(
            entry_id=entry_id,
            key=prop_data.key,
            value_text=prop_data.value_text
        )
        session.add(prop)
        new_props.append(prop)
    
    session.commit()
    for prop in new_props:
        session.refresh(prop)
    
    return new_props


@router.delete("/{entry_id}/props/{key}")
def delete_entry_prop(
    entry_id: int,
    key: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific property from an entry"""
    prop = session.query(EntryPropModel).filter(
        EntryPropModel.entry_id == entry_id,
        EntryPropModel.key == key
    ).first()
    
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    session.delete(prop)
    session.commit()
    return {"message": "Property deleted successfully"}


# Entry Media endpoints
@router.post("/{entry_id}/media", response_model=EntryMedia)
async def upload_media(
    entry_id: int,
    file: UploadFile = File(...),
    kind: Optional[Literal["image", "video", "audio", "doc"]] = Form(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Upload media file for an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    file_info = await store_upload(file, kind)
    
    media = EntryMediaModel(
        entry_id=entry_id,
        kind=file_info["kind"],
        file_path=file_info["file_path"],
        width=file_info.get("width"),
        height=file_info.get("height"),
        meta_json=None  # Could store additional metadata as JSON
    )
    
    session.add(media)
    session.commit()
    session.refresh(media)
    # Return with public URL for client
    return EntryMedia(
        id=media.id,
        entry_id=media.entry_id,
        kind=media.kind,
        file_path=public_url(media.file_path),
        width=media.width,
        height=media.height,
        duration=media.duration,
        meta_json=media.meta_json,
    )


@router.get("/{entry_id}/media", response_model=List[EntryMedia])
def get_entry_media(
    entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Get media files for an entry"""
    entry = session.query(EntryModel).filter(EntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )
    
    items = session.query(EntryMediaModel).filter(EntryMediaModel.entry_id == entry_id).all()
    # Map file_path to public URL for client
    return [
        EntryMedia(
            id=m.id,
            entry_id=m.entry_id,
            kind=m.kind,
            file_path=public_url(m.file_path),
            width=m.width,
            height=m.height,
            duration=m.duration,
            meta_json=m.meta_json,
        )
        for m in items
    ]


@router.delete("/{entry_id}/media/{media_id}")
def delete_media(
    entry_id: int,
    media_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Delete media file from an entry"""
    media = session.query(EntryMediaModel).filter(
        EntryMediaModel.id == media_id,
        EntryMediaModel.entry_id == entry_id
    ).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Delete physical file
    delete_upload(media.file_path)
    
    # Delete database record
    session.delete(media)
    session.commit()
    return {"message": "Media deleted successfully"}
