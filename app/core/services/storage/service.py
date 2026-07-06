from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.services.storage.dtos import UploadFile, UploadFilePost, UploadFilePostResponse


@dataclass
class StorageService(ABC):
    @abstractmethod
    async def upload_put_url(self, bucket_name: str, file_key: str, expires: int) -> str:
        ...

    @abstractmethod
    async def upload_post_file(self, upload_file_post: UploadFilePost) -> UploadFilePostResponse:
        ...

    @abstractmethod
    async def upload_file(self, upload_file: UploadFile) -> str:
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
    ) -> str:
        ...

    @abstractmethod
    async def download(self, bucket_name: str, file_key: str) -> bytes:
        ...

    @abstractmethod
    async def download_range(self, bucket_name: str, file_key: str, offset: int, length: int) -> bytes:
        ...

    @abstractmethod
    def get_public_url_object(self, bucket: str, file_key: str) -> str: ...
