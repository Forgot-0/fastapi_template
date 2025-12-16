from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class BaseStorageService(ABC):
    @abstractmethod
    async def upload_put_url(self, bucket_name: str, file_key: str, expires: int) -> str:
        ...

    @abstractmethod
    async def upload_post_file(self, bucket_name: str, file_name: str, expires: int) -> dict[str, str]:
        ...

    @abstractmethod
    async def upload_file(
        self,
        bucket_name: str,
        file_content: BinaryIO,
        file_key: str,
        size: int,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None
    ) -> str:
        ...

    @abstractmethod
    async def delete_file(
        self,
        bucket_name: str,
        file_key: str
    ) -> bool:
        ...

    @abstractmethod
    async def generate_presigned_url(
        self,
        bucket_name: str,
        file_key: str,
        expires: int = 3600,
    ) -> str | None:
        ...

    @abstractmethod
    async def download(self, bucket_name: str, file_key: str) -> bytes:
        ...

    @abstractmethod
    def get_public_url(self, bucket: str, file_key: str) -> str: ...