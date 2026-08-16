from fastapi import APIRouter, status, UploadFile, File
from uuid import uuid4

from app.config.settings import settings
from app.dependencies.auth import AdminRequiredDep
from app.schemas.images import UploadResBody
from app.utils.image import validate_image
from app.utils.url import static_url_builder

router = APIRouter(prefix="/images", tags=["Images"])



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UploadResBody)
async def upload_image(
    _: AdminRequiredDep,
    file: UploadFile = File(...),
):
    validate_image(file)

    ext = file.filename.split(".")[-1].lower()
    dest_filename = f"{uuid4().hex}.{ext}"
    dest_filepath = settings.UPLOAD_DIR / dest_filename

    CHUNK_SIZE_BYTES = 1024 * 1024  # 1 MB
    with open(dest_filepath, "wb") as buffer:
        while chunk := await file.read(CHUNK_SIZE_BYTES):
            buffer.write(chunk)

    image_url = static_url_builder.build(path=dest_filename)
    return UploadResBody(url=image_url)
