import mimetypes
import os
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from verifyd.api.deps import get_current_user
from verifyd.config import get_settings
from verifyd.core.errors import ValidationError
from verifyd.db.models.user import User
from verifyd.schemas.upload import PresignUploadRequest, PresignUploadResponse
from verifyd.storage.storage import get_storage, validate_magic_bytes

router = APIRouter(prefix="/uploads", tags=["Uploads"])
settings = get_settings()


@router.post("/presign", response_model=PresignUploadResponse)
async def presign_upload(
    req: PresignUploadRequest,
    current_user: User = Depends(get_current_user),
):
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if req.size_bytes > max_bytes:
        raise ValidationError(f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB")

    allowed_types = ["application/pdf", "video/mp4", "video/quicktime", "video/webm", "video/x-matroska"]
    if req.content_type not in allowed_types:
        raise ValidationError(f"Content type '{req.content_type}' is not supported. Allowed: {', '.join(allowed_types)}")

    storage = get_storage()
    upload_url, file_key = storage.generate_presigned_upload(
        filename=req.filename,
        content_type=req.content_type,
        size_bytes=req.size_bytes,
    )

    return PresignUploadResponse(
        url=upload_url,
        file_key=file_key,
        fields={},
        headers={"Content-Type": req.content_type},
    )


@router.put("/direct/{file_path:path}")
async def direct_upload(file_path: str, request: Request):
    """Direct upload receiver for local filesystem storage."""
    body = await request.body()
    if not validate_magic_bytes(body, file_path):
        raise ValidationError("Uploaded file failed binary magic byte validation.")

    storage = get_storage()
    storage.save_file(file_path, body)
    return {"message": "File uploaded successfully", "file_key": file_path}


@router.get("/files/{file_path:path}")
async def serve_file(file_path: str):
    """Serves stored local files with appropriate media types."""
    storage = get_storage()
    content = storage.get_file_content(file_path)
    if not content:
        raise HTTPException(status_code=404, detail="File not found")

    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    return Response(content=content, media_type=content_type)
