from fastapi import HTTPException, status, UploadFile
from PIL import Image
import os

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE_MB = 10


def validate_image(file: UploadFile) -> str:
    # Validate extension
    ext = (
        file.filename.split(".")[-1].lower()
        if file.filename and "." in file.filename
        else ""
    )
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate MIME type
    mime_type = file.content_type
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{mime_type}'. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # Validate file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit",
        )

    # Validate content
    try:
        with Image.open(file.file) as img:
            img.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid or corrupted image file content",
        )
    finally:
        file.file.seek(0)
