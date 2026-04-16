import asyncio
import logging
import mimetypes
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import timedelta

from minio import Minio, S3Error
from minio.datatypes import PostPolicy
from minio.sse import SseS3

from app.core.configs.app import app_config
from app.core.services.storage.aminio.policy import Policy
from app.core.services.storage.dtos import UploadFile, UploadFilePost, UploadFilePostResponse
from app.core.services.storage.service import StorageService
from app.core.utils import now_utc

logger = logging.getLogger(__name__)


@dataclass
class MinioStorageService(StorageService):
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

    async def upload_post_file(self, upload_file_post: UploadFilePost) -> UploadFilePostResponse:
        post_policy = PostPolicy(
            bucket_name=upload_file_post.bucket_name,
            expiration=now_utc() + timedelta(seconds=upload_file_post.expires)
        )

        if upload_file_post.content_type:
            if upload_file_post.content_type.equals:
                post_policy.add_equals_condition("Content-Type", upload_file_post.content_type.text)
            else:
                post_policy.add_starts_with_condition("Content-Type", upload_file_post.content_type.text)
        else:
            content_type, _ = mimetypes.guess_type(upload_file_post.file_key)
            content_type = content_type or "application/octet-stream"
            post_policy.add_equals_condition("Content-Type", content_type)

        post_policy.add_starts_with_condition("key", upload_file_post.file_key)
        post_policy.add_content_length_range_condition(
            0, upload_file_post.size_upper_limit
        )

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(
            self.thread_executor,
            func=lambda: self.client.presigned_post_policy(
                policy=post_policy
            )
        )
        return UploadFilePostResponse(
            url=self.get_puclic_url(upload_file_post.bucket_name),
            fields=data
        )

    async def upload_file(self, upload_file: UploadFile) -> str:
        if upload_file.bucket_name not in self.bucket_policy:
            raise ValueError("No exist bucket")

        if not upload_file.content_type:
            content_type, _ = mimetypes.guess_type(upload_file.file_key)
            content_type = content_type or "application/octet-stream"

        s3_metadata = {
            "uploaded_at": now_utc().isoformat(),
        }

        if upload_file.metadata:
            s3_metadata.update({k: str(v) for k, v in upload_file.metadata.items()})

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            self.thread_executor,
            func= lambda: self.client.put_object(
                bucket_name=upload_file.bucket_name,
                object_name=upload_file.file_key,
                data=upload_file.file_content,
                length=upload_file.size,
                content_type=content_type,
                metadata=s3_metadata, # type: ignore
                sse=SseS3() if self.bucket_policy[upload_file.bucket_name] == Policy.NONE else None,
            )
        )

        logger.info("File uploaded successfully", extra={
            "file_key": upload_file.file_key,
            "bucket_name": upload_file.bucket_name}
        )

        return (
            upload_file.file_key
            if self.bucket_policy[upload_file.bucket_name] == Policy.NONE
            else self.get_public_url_object(upload_file.bucket_name, upload_file.file_key)
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
        response=None
        try:
            response = self.client.get_object(bucket_name=bucket_name, object_name=file_key)
            return response.read()
        except Exception as e:
            raise e
        finally:
            if response:
                response.close()
                response.release_conn()

    def get_public_url_object(self, bucket: str, file_key: str) -> str:
        return f"{app_config.STORAGE_PUBLIC_URL}/{bucket}/{file_key}"

    def get_puclic_url(self, bucket: str) -> str:
        return f"{app_config.STORAGE_PUBLIC_URL}/{bucket}"

