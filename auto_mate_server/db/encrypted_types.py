"""SQLAlchemy types for encrypted columns."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

from auto_mate_server.crypto import decrypt_field, encrypt_field


class EncryptedText(TypeDecorator[str | None]):
    """Store values encrypted at rest; expose plaintext to application code."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        return encrypt_field(value)

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        return decrypt_field(value)
