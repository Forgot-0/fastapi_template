import asyncio
import logging
import mimetypes
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import timedelta
from typing import BinaryIO

from minio import Minio, S3Error
from minio.datatypes import PostPolicy
from minio.sse import SseS3

from app.core.configs.app import app_config
from app.core.services.storage.aminio.policy import Policy
from app.core.services.storage.service import BaseStorageService
from app.core.utils import now_utc

logger = logging.getLogger(__name__)


@dataclass
class MinioStorageService(BaseStorageService):
    client: Minio
    bucket_policy: dict[str, Policy]

    max_thread: int = field(default=20)
    thread_executor: ThreadPoolExecutor = field(init=False)

    def __post_init__(self) -> None:
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_thread, thread_name_prefix="storage-worker")
        self.create_bucket()

    def create_bucket(self) -> None:
        for bucket in self.bucket_policy:
            try:
                policy = self.bucket_policy[bucket]
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)

                logger.info("Bucket created", extra={"bucket_name": bucket})

                self.client.set_bucket_policy(bucket, policy.bucket(bucket))
                logger.info("Policy set for bucket", extra={"bucket_name": bucket})
            except S3Error as e:
                logger.exception("Failed to create bucket and policy", extra={"bucket": bucket, "error": e})

    async def upload_put_url(self, bucket_name: str, file_key: str, expires: int) -> str:
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            self.thread_executor,
            func=lambda: self.client.presigned_put_object(
                bucket_name=bucket_name,
                object_name=file_key,
                expires=timedelta(seconds=expires)
            )
        )
        return url

    async def upload_post_file(self, bucket_name: str, file_name: str, expires: int) -> dict[str, str]:
        post_policy = PostPolicy(
            bucket_name=bucket_name,
            expiration=now_utc() + timedelta(seconds=expires)
        )

        content_type, _ = mimetypes.guess_type(file_name)
        content_type = content_type or "application/octet-stream"

        post_policy.add_equals_condition("key", file_name)
        post_policy.add_equals_condition("Content-Type", content_type)

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(
            self.thread_executor,
            func=lambda: self.client.presigned_post_policy(
                policy=post_policy
            )
        )
        return data

    async def upload_file(
        self,
        bucket_name: str,
        file_content: BinaryIO,
        file_key: str,
        size: int,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None
    ) -> str:
        if bucket_name not in self.bucket_policy:
            raise ValueError("No exist bucket")

        if not content_type:
            content_type, _ = mimetypes.guess_type(file_key)
            content_type = content_type or "application/octet-stream"

        s3_metadata = {
            "uploaded_at": now_utc().isoformat(),
        }

        if metadata:
            s3_metadata.update({k: str(v) for k, v in metadata.items()})

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self.thread_executor,
            func= lambda: self.client.put_object(
                bucket_name=bucket_name,
                object_name=file_key,
                data=file_content,
                length=size,
                content_type=content_type,
                metadata=s3_metadata, # type: ignore
                sse=SseS3() if self.bucket_policy[bucket_name] == Policy.NONE else None,
            )
        )

        logger.info("File uploaded successfully", extra={"file_key": file_key, "bucket_name": bucket_name})
        return (
            file_key 
            if self.bucket_policy[bucket_name] == Policy.NONE
            else self.get_public_url(bucket_name, file_key)
        )

    async def delete_file(self, bucket_name: str, file_key: str) -> bool:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self.thread_executor,
            lambda: self.client.remove_object(
                bucket_name=bucket_name,
                object_name=file_key
            )
        )

        logger.info("File deleted successfully", extra={"file_key": file_key})
        return True

    async def generate_presigned_url(self, bucket_name: str, file_key: str, expires: int = 3600) -> str:
        loop = asyncio.get_running_loop()
        url = await loop.run_in_executor(
            self.thread_executor,
            lambda: self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=file_key,
                expires=timedelta(seconds=expires)
            )
        )

        return url

    async def download(self, bucket_name: str, file_key: str) -> bytes:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.thread_executor,
            lambda: self._download_file_sync(bucket_name=bucket_name, file_key=file_key)
        )
        return result

    def _download_file_sync(self, bucket_name: str, file_key: str) -> bytes:
        try:
            response = self.client.get_object(bucket_name=bucket_name, object_name=file_key)
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def get_public_url(self, bucket: str, file_key: str) -> str:
        return f"{app_config.STORAGE_PUBLIC_URL}/{bucket}/{file_key}"
