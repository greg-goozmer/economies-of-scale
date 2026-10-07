from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from minio import Minio

from core.config import settings


CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
}


def _object_key(file: UploadFile, kind: str) -> str:
    extension = CONTENT_TYPES.get(file.content_type or "")
    if extension is None or not (file.content_type or "").startswith(kind + "/"):
        raise HTTPException(422, f"Expected a {kind} file")
    return f"cost_{uuid4().hex}{extension}"


def upload_cost_media(image: UploadFile, video: UploadFile) -> tuple[str, str]:
    """Upload both actual files; remove uploaded objects if the second fails."""
    image_key = _object_key(image, "image")
    video_key = _object_key(video, "video")
    client = Minio(settings.MINIO_ENDPOINT, access_key=settings.MINIO_ROOT_USER,
                   secret_key=settings.MINIO_ROOT_PASSWORD, secure=False)
    uploaded = []
    try:
        for file, key in ((image, image_key), (video, video_key)):
            stream = file.file
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(0)
            if size == 0:
                raise HTTPException(422, "Media file is empty")
            client.put_object(settings.MINIO_BUCKET, key, stream, size,
                              content_type=file.content_type)
            uploaded.append(key)
    except Exception:
        for key in uploaded:
            client.remove_object(settings.MINIO_BUCKET, key)
        raise
    root = settings.MINIO_PUBLIC_URL.rstrip("/")
    return (f"{root}/{settings.MINIO_BUCKET}/{image_key}",
            f"{root}/{settings.MINIO_BUCKET}/{video_key}")


def remove_cost_media(urls: tuple[str, str]) -> None:
    client = Minio(settings.MINIO_ENDPOINT, access_key=settings.MINIO_ROOT_USER,
                   secret_key=settings.MINIO_ROOT_PASSWORD, secure=False)
    for url in urls:
        client.remove_object(settings.MINIO_BUCKET, Path(url).name)
