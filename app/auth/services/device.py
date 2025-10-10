import hashlib
from dataclasses import dataclass

from fastapi import Request
import orjson
from user_agents import parse

from app.auth.schemas.token import DeviceInformation

def generate_device_info(request: Request) -> DeviceInformation:
    user_agent_string = request.headers.get("user-agent", "")
    headers = dict(request.headers)

    ua = parse(user_agent_string)

    browser = f"{ua.browser.family} {ua.browser.version_string}"
    os = f"{ua.os.family} {ua.os.version_string}"

    simplified_ua = f"{browser} on {os}"[:100]

    device_info = {
        "browser_family": ua.browser.family,
        "os_family": ua.os.family,
        "device": ua.get_device(),
        "accept_lang": headers.get("accept-language", ""),
        "accept_encoding": headers.get("accept-encoding", ""),
    }

    fingerprint_json = orjson.dumps(device_info)
    device_hash = hashlib.sha256(fingerprint_json).hexdigest()

    device_data = DeviceInformation(
        device_info=fingerprint_json,
        device_id=device_hash,
        user_agent=simplified_ua,
    )

    return device_data

def verify_device(
    request: Request, jwt_device_data: dict[str, str]
) -> bool:
    current_device = generate_device_info(request)

    return current_device.device_id == jwt_device_data.get("di")
