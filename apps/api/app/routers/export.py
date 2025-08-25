import io
import zipfile
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..db import get_session
from ..models import User, Hobby, HobbyType, Entry, EntryMedia, EntryProp

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/")
def export_data(
    format: str = "zip",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Export all data as ZIP archive or JSON"""
    
    if format == "json":
        return export_json(session)
    elif format == "zip":
        return export_zip(session)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'json' or 'zip'"
        )


def export_json(session: Session):
    """Export data as JSON"""
    # Get all data
    users = session.query(User).all()
    hobbies = session.query(Hobby).all()
    hobby_types = session.query(HobbyType).all()
    entries = session.query(Entry).all()
    entry_media = session.query(EntryMedia).all()
    entry_props = session.query(EntryProp).all()
    
    # Convert to dictionaries
    data = {
        "version": "1.0",
        "export_date": datetime.now(timezone.utc).isoformat(),
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "bio": u.bio,
                "avatar_path": u.avatar_path,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ],
        "hobbies": [
            {
                "id": h.id,
                "name": h.name,
                "color": h.color,
                "icon": h.icon,
                "parent_id": h.parent_id
            }
            for h in hobbies
        ],
        "hobby_types": [
            {
                "id": ht.id,
                "key": ht.key,
                "title": ht.title,
                "schema_json": ht.schema_json
            }
            for ht in hobby_types
        ],
        "entries": [
            {
                "id": e.id,
                "hobby_id": e.hobby_id,
                "type_key": e.type_key,
                "title": e.title,
                "description": e.description,
                "tags": e.tags,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "updated_at": e.updated_at.isoformat() if e.updated_at else None
            }
            for e in entries
        ],
        "entry_media": [
            {
                "id": em.id,
                "entry_id": em.entry_id,
                "kind": em.kind,
                "file_path": em.file_path,
                "width": em.width,
                "height": em.height,
                "duration": em.duration,
                "meta_json": em.meta_json
            }
            for em in entry_media
        ],
        "entry_props": [
            {
                "id": ep.id,
                "entry_id": ep.entry_id,
                "key": ep.key,
                "value_text": ep.value_text
            }
            for ep in entry_props
        ]
    }
    
    json_str = json.dumps(data, indent=2)
    
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=hobby-showcase-export.json"}
    )


def export_zip(session: Session):
    """Export data as ZIP archive with database export and uploads"""
    
    # Create in-memory ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add JSON export (reuse serialization logic)
        json_resp = export_json(session)
        zf.writestr("data.json", json_resp.body)
        
        # Add database file if it exists
        db_path_str = os.getenv("DB_PATH", "./data/app.db")
        db_path = Path(db_path_str)
        if db_path.exists():
            zf.write(db_path, "app.db")
        
        # Add upload files
        uploads_path_str = os.getenv("UPLOAD_DIR", "./uploads")
        uploads_path = Path(uploads_path_str)
        if uploads_path.exists():
            for file_path in uploads_path.rglob("*"):
                if file_path.is_file():
                    archive_path = f"uploads/{file_path.relative_to(uploads_path)}"
                    zf.write(file_path, archive_path)
        
        # Add metadata
        metadata = {
            "export_date": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "format": "hobby-showcase-backup"
        }
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        io.BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=hobby-showcase-backup.zip"}
    )
