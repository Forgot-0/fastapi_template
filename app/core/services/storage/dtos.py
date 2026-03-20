from dataclasses import dataclass, field
from typing import BinaryIO


@dataclass
class UploadFile:
    bucket_name: str
    file_content: BinaryIO
    file_key: str
    size: int
    content_type: str | None = field(default=None)
    metadata: dict[str, str] | None = field(default=None)


@dataclass
class ContentTypeFilter:
    text: str
    equals: bool = field(default=True)


@dataclass
class UploadFilePost:
    bucket_name: str
    file_key: str
    expires: int

    size_upper_limit: int

    content_type: ContentTypeFilter | None = field(default=None)
    size_lower_limit: int = field(default=0)


@dataclass
class UploadFilePostResponse:
    url: str
    fields: dict[str, str]
