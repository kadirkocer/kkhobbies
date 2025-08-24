import os
import re
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Set
from fastapi import UploadFile, HTTPException, status

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

# Security constants
ALLOWED_MIME_TYPES: Set[str] = {
    "image/png", "image/jpeg", "image/webp",
    "video/mp4", "audio/mpeg", "application/pdf"
}

SIZE_LIMIT = 50 * 1024 * 1024  # 50MB

def _resolve_upload_dir() -> Path:
    base_dir = Path(__file__).resolve().parent  # apps/api/app/services
    repo_root = base_dir.parent.parent.parent.parent  # go to project root
    env_path = os.getenv("UPLOAD_DIR", "uploads")
    # Normalize and make absolute relative to repo root if not absolute
    up = Path(env_path)
    if not up.is_absolute():
        up = (repo_root / up).resolve()
    return up

UPLOAD_DIR: Path = _resolve_upload_dir()

# Regex for safe filenames (alphanumeric, dots, hyphens, underscores)
SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')


def secure_filename(filename: str) -> str:
    """
    Generate a secure filename by removing unsafe characters and preventing path traversal.
    """
    if not filename:
        return "unnamed"
    
    # Get just the filename part (no path)
    basename = Path(filename).name
    
    # Keep only safe characters
    safe_chars = []
    for char in basename:
        if char.isalnum() or char in '.-_':
            safe_chars.append(char)
        else:
            safe_chars.append('_')
    
    safe_name = ''.join(safe_chars)
    
    # Ensure it doesn't start with a dot (hidden file)
    if safe_name.startswith('.'):
        safe_name = 'file' + safe_name
    
    # Ensure it's not empty after sanitization
    if not safe_name or safe_name == '.':
        safe_name = 'unnamed_file'
    
    # Limit length
    if len(safe_name) > 100:
        # Keep extension if present
        if '.' in safe_name:
            name_part, ext_part = safe_name.rsplit('.', 1)
            safe_name = name_part[:95] + '.' + ext_part
        else:
            safe_name = safe_name[:100]
    
    return safe_name


def detect_mime_type(content: bytes, filename: str) -> Optional[str]:
    """
    Detect MIME type from file content and validate against filename extension.
    """
    mime_type = None
    
    # Try magic library for content-based detection
    if HAS_MAGIC:
        try:
            mime_type = magic.from_buffer(content[:2048], mime=True)
        except Exception:
            pass
    
    # Fallback: basic signature detection for common types
    if not mime_type:
        if content.startswith(b'\x89PNG\r\n\x1a\n'):
            mime_type = "image/png"
        elif content.startswith(b'\xff\xd8\xff'):
            mime_type = "image/jpeg"
        elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
            mime_type = "image/webp"
        elif content.startswith(b'\x00\x00\x00\x18ftypmp4') or content.startswith(b'\x00\x00\x00\x20ftypmp4'):
            mime_type = "video/mp4"
        elif content.startswith(b'ID3') or content.startswith(b'\xff\xfb'):
            mime_type = "audio/mpeg"
        elif content.startswith(b'%PDF-'):
            mime_type = "application/pdf"
    
    return mime_type


def validate_file_security(content: bytes, filename: str, kind: Optional[str]) -> str:
    """
    Validate file for security: MIME type, size, and filename safety.
    
    Args:
        content: File content bytes
        filename: Original filename
        kind: Optional file kind hint
        
    Returns:
        str: Detected file kind
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file size
    if len(content) > SIZE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {SIZE_LIMIT // 1024 // 1024}MB"
        )
    
    # Empty file check
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file not allowed"
        )
    
    # Detect MIME type from content
    mime_type = detect_mime_type(content, filename)
    
    if not mime_type or mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )
    
    # Map MIME type to kind
    if mime_type.startswith('image/'):
        detected_kind = 'image'
    elif mime_type.startswith('video/'):
        detected_kind = 'video'
    elif mime_type.startswith('audio/'):
        detected_kind = 'audio'
    elif mime_type == 'application/pdf':
        detected_kind = 'doc'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )
    
    # If kind was provided, verify it matches
    if kind and kind != detected_kind:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type mismatch: expected {kind}, got {detected_kind}"
        )
    
    return detected_kind


async def store_upload(file: UploadFile, kind: Optional[str] = None) -> Dict[str, Any]:
    """
    Securely store an uploaded file with validation.
    
    Args:
        file: FastAPI UploadFile object
        kind: Optional file kind hint ('image', 'video', 'audio', 'doc')
        
    Returns:
        Dict with file path and metadata
        
    Raises:
        HTTPException: If validation fails
    """
    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read file"
        )
    
    # Validate file security
    validated_kind = validate_file_security(content, file.filename or "", kind)
    
    # Generate secure filename
    original_filename = file.filename or "unnamed"
    safe_name = secure_filename(original_filename)
    extension = Path(safe_name).suffix.lower()
    
    # Generate unique ID and create final filename
    unique_id = str(uuid.uuid4())
    final_filename = f"{unique_id}{extension}"
    
    # Create subdirectory for file kind
    kind_dir = UPLOAD_DIR / validated_kind
    kind_dir.mkdir(exist_ok=True)
    
    # Final file path
    file_path = kind_dir / final_filename
    
    # Prevent path traversal by checking resolved path is within upload dir
    resolved_path = file_path.resolve()
    upload_dir_resolved = Path(UPLOAD_DIR).resolve()
    
    if not str(resolved_path).startswith(str(upload_dir_resolved)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Prepare response
    file_info = {
        "file_path": str(file_path),
        "kind": validated_kind,
        "original_filename": original_filename,
        "size": len(content),
        "mime_type": detect_mime_type(content, original_filename)
    }
    
    # Get image dimensions if it's an image
    if validated_kind == "image":
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                file_info["width"] = img.width
                file_info["height"] = img.height
        except Exception:
            # Not critical if we can't get dimensions
            pass
    
    return file_info


def delete_upload(file_path: str) -> bool:
    """
    Safely delete an uploaded file.
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        path = Path(file_path)
        
        # Ensure path is within upload directory (prevent deletion outside)
        resolved_path = path.resolve()
        upload_dir_resolved = UPLOAD_DIR.resolve()
        
        if not str(resolved_path).startswith(str(upload_dir_resolved)):
            return False
        
        if path.exists() and path.is_file():
            path.unlink()
            return True
    except Exception:
        pass
    
    return False


def public_url(file_path: str) -> str:
    """Build a public URL path for a stored upload.

    Returns a path under `/api/uploads/...` suitable for the frontend.
    """
    try:
        p = Path(file_path)
        # If absolute, make it relative to the upload dir
        if p.is_absolute():
            rel = p.resolve().relative_to(UPLOAD_DIR.resolve())
        else:
            # Treat as relative under upload dir
            rel = p
        return f"/api/uploads/{rel.as_posix()}"
    except Exception:
        # Fallback best-effort
        return f"/api/uploads/{Path(file_path).name}"
