"""Encrypt integration secrets at rest (Fernet: AES-128 + HMAC)."""

from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from auto_mate_server.secret_key_loader import load_or_create_fernet_key


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    return Fernet(load_or_create_fernet_key())


def encrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "":
        return ""
    token = _fernet().encrypt(value.encode("utf-8"))
    return token.decode("ascii")


def decrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    if value == "":
        return ""
    try:
        return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, TypeError):
        # Legacy plaintext rows before encryption was enabled
        return value
