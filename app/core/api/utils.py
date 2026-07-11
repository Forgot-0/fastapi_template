from starlette.requests import Request
from starlette.websockets import WebSocket


def get_ip_from_request(request: Request | WebSocket) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        assert request.client is not None
        ip = request.client.host

    return ip
