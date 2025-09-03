from app.core.di.broker import BrokerProvider
from app.core.di.cache import CacheProvider
from app.core.di.db import DBProvider
from app.core.di.events import EventProvider
from app.core.di.mail import MailProvider
from app.core.di.mediator import MediatorProvider
from app.core.di.queue import QueueProvider


def get_core_providers():
    return [
        BrokerProvider(),
        DBProvider(),
        CacheProvider(),
        MediatorProvider(),
        EventProvider(),
        QueueProvider(),
        MailProvider(),
    ]