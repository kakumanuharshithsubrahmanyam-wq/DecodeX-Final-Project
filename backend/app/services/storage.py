from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import httpx

from app.config import get_settings
from app.core.exceptions import AppError

logger = logging.getLogger("rtgs.storage")


def safe_filename(name: str) -> str:
    base = name.split("/")[-1].split("\\")[-1]
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return cleaned[:120] or "upload.bin"


def build_object_path(grievance_id: UUID, attachment_id: UUID, file_name: str) -> str:
    return f"{grievance_id}/{attachment_id}/{safe_filename(file_name)}"


class StorageClient:
    async def create_signed_upload_url(self, object_path: str, content_type: str, expires_in: int) -> str:
        raise NotImplementedError

    async def create_signed_download_url(self, object_path: str, expires_in: int) -> str:
        raise NotImplementedError

    async def remove_object(self, object_path: str) -> None:
        raise NotImplementedError


class SupabaseStorageClient(StorageClient):
    def __init__(self, base_url: str, service_key: str, bucket: str):
        self.base_url = base_url.rstrip("/")
        self.service_key = service_key
        self.bucket = bucket

    async def create_signed_upload_url(self, object_path: str, content_type: str, expires_in: int) -> str:
        url = f"{self.base_url}/storage/v1/object/upload/sign/{self.bucket}/{object_path}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.service_key}", "apikey": self.service_key},
                json={"expiresIn": expires_in, "contentType": content_type},
            )
        if resp.status_code >= 400:
            logger.warning("Storage sign upload failed: %s", resp.status_code)
            raise AppError("STORAGE_ERROR", "Unable to create upload URL", 502)
        data = resp.json()
        signed = data.get("signedURL") or data.get("signedUrl")
        if not signed:
            raise AppError("STORAGE_ERROR", "Invalid storage response", 502)
        if signed.startswith("/"):
            return f"{self.base_url}{signed}"
        return signed

    async def create_signed_download_url(self, object_path: str, expires_in: int) -> str:
        url = f"{self.base_url}/storage/v1/object/sign/{self.bucket}/{object_path}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.service_key}", "apikey": self.service_key},
                json={"expiresIn": expires_in},
            )
        if resp.status_code >= 400:
            raise AppError("STORAGE_ERROR", "Unable to create download URL", 502)
        data = resp.json()
        signed = data.get("signedURL") or data.get("signedUrl")
        if signed and signed.startswith("/"):
            return f"{self.base_url}{signed}"
        return signed

    async def remove_object(self, object_path: str) -> None:
        url = f"{self.base_url}/storage/v1/object/{self.bucket}/{object_path}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            await client.delete(url, headers={"Authorization": f"Bearer {self.service_key}", "apikey": self.service_key})


class MockStorageClient(StorageClient):
    async def create_signed_upload_url(self, object_path: str, content_type: str, expires_in: int) -> str:
        return f"https://storage.mock/upload/{object_path}?expires={expires_in}"

    async def create_signed_download_url(self, object_path: str, expires_in: int) -> str:
        return f"https://storage.mock/download/{object_path}?expires={expires_in}"

    async def remove_object(self, object_path: str) -> None:
        return None


def get_storage_client() -> StorageClient:
    settings = get_settings()
    if settings.supabase_url and settings.supabase_service_role_key:
        return SupabaseStorageClient(
            settings.supabase_url,
            settings.supabase_service_role_key,
            settings.supabase_storage_bucket,
        )
    return MockStorageClient()


def upload_expires_at(seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=seconds)
