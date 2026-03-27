"""Normalize and validate integration payloads by vendor type."""

from common.enums import IntegrationType
from auto_mate_server.schemas import IntegrationCreateRequest


def integration_credentials_for_db(
    itype: IntegrationType, payload: IntegrationCreateRequest
) -> dict[str, str | None]:
    if itype == IntegrationType.TINYTUYA:
        return {
            "access_key": payload.access_key.strip() if payload.access_key else None,
            "access_key_secret": payload.access_key_secret.strip() if payload.access_key_secret else None,
            "device_id": payload.device_id,
            "username": None,
            "password": None,
        }
    return {
        "access_key": None,
        "access_key_secret": None,
        "username": payload.username.strip() if payload.username else None,
        "password": payload.password.strip() if payload.password else None,
    }
