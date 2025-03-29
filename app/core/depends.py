from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_session
from app.core.services.cache.base import CacheServiceInterface
from app.core.services.cache.deps import get_cache_service, get_cached_decorator
from app.core.services.log.depends import get_log_service
from app.core.services.mail.depends import get_mail_service
from app.core.services.mail.service import MailServiceInterface
from app.core.services.queue.depends import get_queue_service, get_queued_decorator
from app.core.services.queue.service import QueueServiceInterface


logger = get_log_service()


Asession = Annotated[AsyncSession, Depends(get_session)]
QueueService = Annotated[QueueServiceInterface, Depends(get_queue_service)]
MailService = Annotated[MailServiceInterface, Depends(get_mail_service)]
CacheService = Annotated[CacheServiceInterface, Depends(get_cache_service)]

queued = get_queued_decorator()
cached = get_cached_decorator()
