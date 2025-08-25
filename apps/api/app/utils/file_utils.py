import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from PIL import Image

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

ALLOWED_EXTENSIONS = {
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "video": [".mp4", ".mov", ".avi", ".webm"],
    "audio": [".mp3", ".wav", ".ogg", ".m4a"],
    "doc": [".pdf", ".txt", ".md", ".docx"]
}

ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
    "video": ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/x-m4a"],
    "doc": ["application/pdf", "text/plain", "text/markdown", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
}


def ensure_upload_dir():
    """Ensure upload directory exists"""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def get_file_kind(filename: str, content: bytes) -> str | None:
    """Determine file kind based on extension and MIME type"""
    extension = Path(filename).suffix.lower()

    mime_type = None
    if HAS_MAGIC:
        try:
            mime_type = magic.from_buffer(content, mime=True)
        except:
            mime_type = None

    for kind, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            if mime_type and mime_type in ALLOWED_MIME_TYPES[kind]:
                return kind
            elif not mime_type:  # Fallback to extension if magic fails
                return kind

    return None


async def save_upload_file(file: UploadFile, kind: str | None = None) -> dict[str, Any]:
    """Save uploaded file and return file info"""
    ensure_upload_dir()

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Determine file kind if not provided
    if not kind:
        kind = get_file_kind(file.filename or "", content)
        if not kind:
            raise ValueError("Unsupported file type")

    # Generate unique filename
    file_id = str(uuid.uuid4())
    extension = Path(file.filename or "").suffix.lower()
    filename = f"{file_id}{extension}"

    # Create subdirectory for file kind
    kind_dir = Path(UPLOAD_DIR) / kind
    kind_dir.mkdir(exist_ok=True)

    file_path = kind_dir / filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(content)

    # Get file metadata
    file_info = {
        "file_path": str(file_path.relative_to(Path(UPLOAD_DIR).parent)),
        "kind": kind,
        "filename": file.filename,
        "size": len(content)
    }

    # Get additional metadata for images
    if kind == "image":
        try:
            with Image.open(file_path) as img:
                file_info["width"] = img.width
                file_info["height"] = img.height
        except:
            pass

    return file_info


def get_file_info(file_path: str) -> dict[str, Any]:
    """Get information about an existing file"""
    full_path = Path(file_path)

    if not full_path.exists():
        raise FileNotFoundError("File not found")

    info = {
        "size": full_path.stat().st_size,
        "extension": full_path.suffix.lower()
    }

    # Try to get MIME type
    if HAS_MAGIC:
        try:
            with open(full_path, "rb") as f:
                content = f.read(1024)  # Read first 1KB for MIME detection
                info["mime_type"] = magic.from_buffer(content, mime=True)
        except:
            pass

    return info


def delete_file(file_path: str) -> bool:
    """Delete a file"""
    try:
        full_path = Path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
    except:
        pass
    return False
