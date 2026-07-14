from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from app.core.events.event import BaseEvent
from app.core.events.service import BaseEventBus
from app.core.services.mail.service import BaseMailService, EmailData
from app.core.services.mail.template import BaseTemplate
from app.core.services.queues.service import QueueResult, QueueResultStatus, QueueService
from app.core.services.queues.task import BaseTask
from app.core.services.storage.dtos import UploadFile, UploadFilePost, UploadFilePostResponse
from app.core.services.storage.service import StorageService


class FakeQueueService(QueueService):
    def __init__(self) -> None:
        self.pushed: list[tuple[type[BaseTask], dict[str, Any]]] = []

    async def push(self, task: type[BaseTask], data: dict[str, Any]) -> str:
        self.pushed.append((task, data))
        return "fake-queue-task-id"

    async def is_ready(self, task_id: str) -> bool:
        return True

    async def get_result(self, task_id: str) -> QueueResult:
        return QueueResult(response=None, status=QueueResultStatus.SUCCESS)

    async def wait_result(
        self,
        task_id: str,
        check_interval: float | None = None,
        timeout: float | None = None,
    ) -> QueueResult:
        return QueueResult(response=None, status=QueueResultStatus.SUCCESS)


class FakeStorageService(StorageService):
    async def upload_put_url(self, bucket_name: str, file_key: str, expires: int) -> str:
        return f"https://storage.test/upload/{bucket_name}/{file_key}?expires={expires}"

    async def upload_post_file(self, upload_file_post: UploadFilePost) -> UploadFilePostResponse:
        return UploadFilePostResponse(url="https://storage.test/post", fields={})

    async def upload_file(self, upload_file: UploadFile) -> str:
        return "etag-test"

    async def delete_file(self, bucket_name: str, file_key: str) -> bool:
        return True

    async def generate_presigned_url(
        self,
        bucket_name: str,
        file_key: str,
        expires: int = 3600,
    ) -> str:
        return f"https://storage.test/download/{bucket_name}/{file_key}?expires={expires}"

    async def download(self, bucket_name: str, file_key: str) -> bytes:
        return b""

    async def download_range(self, bucket_name: str, file_key: str, offset: int, length: int) -> bytes:
        return b""

    def get_public_url_object(self, bucket: str, file_key: str) -> str:
        return f"https://storage.test/public/{bucket}/{file_key}"



@dataclass
class MockMailService(BaseMailService):
    sent_emails: list = field(default_factory=list)

    async def send(self, template: BaseTemplate, email_data: EmailData) -> None:
        self.sent_emails.append({"template": template, "data": email_data})

    async def queue(self, template: BaseTemplate, email_data: EmailData) -> str:
        self.sent_emails.append({"template": template, "data": email_data})
        return "task_id"

    async def send_plain(self, subject: str, recipient: str, body: str) -> None:
        ...

    async def queue_plain(self, subject: str, recipient: str, body: str) -> str:
        return "task_id"



@dataclass
class MockEventBus(BaseEventBus):
    published_events: list[BaseEvent] = field(default_factory=list)

    async def publish(self, events: Iterable[BaseEvent]) -> None:
        self.published_events.extend(events)

