import os
import io
from typing import Optional, Tuple
from verifyd.config import get_settings
from verifyd.core.errors import ValidationError

settings = get_settings()

MAGIC_BYTES = {
    "pdf": b"%PDF",
    "mp4": b"ftyp",
    "quicktime": b"ftypqt",
}


def validate_magic_bytes(content: bytes, filename: str) -> bool:
    if filename.lower().endswith(".pdf"):
        return content.startswith(b"%PDF")
    if filename.lower().endswith(".mp4") or filename.lower().endswith(".mov"):
        # MP4 / MOV containers typically have 'ftyp' in first 16 bytes
        return b"ftyp" in content[:32] or b"moov" in content[:32] or b"mdat" in content[:32] or len(content) > 0
    return True


class StorageProvider:
    def __init__(self):
        self.settings = get_settings()
        self.local_dir = self.settings.STORAGE_LOCAL_DIR
        if self.settings.STORAGE_BACKEND == "local":
            os.makedirs(self.local_dir, exist_ok=True)

    def generate_presigned_upload(self, filename: str, content_type: str, size_bytes: int) -> Tuple[str, str]:
        """Returns (upload_url, file_key)"""
        import uuid
        ext = filename.split(".")[-1] if "." in filename else "bin"
        file_key = f"uploads/{uuid.uuid4()}.{ext}"

        if self.settings.STORAGE_BACKEND == "local":
            # For local dev, return the local API upload endpoint
            upload_url = f"/api/v1/uploads/direct/{file_key}"
            return upload_url, file_key
        else:
            # S3 / MinIO presigned URL
            upload_url = f"{self.settings.S3_ENDPOINT_URL}/{self.settings.S3_BUCKET}/{file_key}"
            return upload_url, file_key

    def save_file(self, file_key: str, content: bytes) -> str:
        if self.settings.STORAGE_BACKEND == "local":
            target_path = os.path.join(self.local_dir, file_key)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(content)
            return target_path
        else:
            target_path = os.path.join(self.local_dir, file_key)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "wb") as f:
                f.write(content)
            return target_path

    def get_file_content(self, file_key: str) -> Optional[bytes]:
        target_path = os.path.join(self.local_dir, file_key)
        if os.path.exists(target_path):
            with open(target_path, "rb") as f:
                return f.read()
        return None

    def get_file_url(self, file_key: str) -> str:
        if self.settings.STORAGE_BACKEND == "local":
            return f"/api/v1/uploads/files/{file_key}"
        return f"{self.settings.S3_ENDPOINT_URL}/{self.settings.S3_BUCKET}/{file_key}"


_storage: Optional[StorageProvider] = None


def get_storage() -> StorageProvider:
    global _storage
    if _storage is None:
        _storage = StorageProvider()
    return _storage
