import os
import io
import boto3
from botocore.config import Config
from typing import Optional, Dict, Any
from backend.app.config import settings


class R2StorageService:
    """
    Cloudflare R2 Object Storage Service (S3-Compatible API).
    Provides raw file ingestion storage, auto-corrected Excel model archiving,
    and generated WP-514 PDF distribution with presigned download URLs.
    Falls back gracefully to local disk when R2 keys are omitted.
    """

    def __init__(self):
        self.bucket_name = settings.R2_BUCKET_NAME
        self.has_r2 = bool(settings.R2_ACCESS_KEY_ID and settings.R2_SECRET_ACCESS_KEY and settings.R2_ACCOUNT_ID)

        if self.has_r2:
            endpoint = settings.R2_ENDPOINT_URL or f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4")
            )
        else:
            self.s3_client = None
            os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)

    def upload_file(self, file_bytes: bytes, object_key: str, content_type: str = "application/octet-stream") -> str:
        """
        Uploads bytes to Cloudflare R2 bucket or local file store.
        Returns the object key or relative URI.
        """
        if self.has_r2 and self.s3_client:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type
            )
            return object_key
        else:
            local_path = os.path.join(settings.LOCAL_STORAGE_DIR, object_key.replace("/", "_"))
            os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_bytes)
            return local_path

    def get_presigned_url(self, object_key: str, expires_in: int = 3600) -> str:
        """
        Generates presigned download URL for R2 object or local API download route.
        """
        if self.has_r2 and self.s3_client:
            try:
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_key},
                    ExpiresIn=expires_in
                )
                return url
            except Exception:
                return f"/api/v1/reports/download/{object_key}"
        else:
            return f"/api/v1/reports/download/{os.path.basename(object_key)}"

    def download_file(self, object_key: str) -> Optional[bytes]:
        """
        Retrieves file bytes from R2 or local storage.
        """
        if self.has_r2 and self.s3_client:
            resp = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
            return resp["Body"].read()
        else:
            local_path = os.path.join(settings.LOCAL_STORAGE_DIR, object_key.replace("/", "_"))
            if not os.path.exists(local_path):
                local_path = os.path.join(settings.LOCAL_STORAGE_DIR, os.path.basename(object_key))
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            return None


r2_service = R2StorageService()
