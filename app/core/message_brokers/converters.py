from dataclasses import asdict
from typing import Any

import orjson

from app.core.events.event import BaseEvent


def convert_event_to_broker_message(event: BaseEvent) -> bytes:
    data = asdict(event)
    data["event_name"] = event.get_name()
    return orjson.dumps(data)

def convert_event_to_json(event: BaseEvent) -> dict[str, Any]:
    return asdict(event)

def convert_dict_to_broker_message(data: dict[str, Any]) -> bytes:
    return orjson.dumps(data)
