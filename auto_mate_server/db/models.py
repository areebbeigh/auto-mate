from datetime import datetime
from typing import Any
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    func,
    Enum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from common.enums import IntegrationType
from auto_mate_server.db.encrypted_types import EncryptedText


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    integrations: Mapped[list["Integration"]] = relationship(back_populates="user")
    devices: Mapped[list["Device"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"


class Integration(TimestampMixin, Base):
    __tablename__ = "integrations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="integrations")
    type: Mapped[IntegrationType] = mapped_column(Enum(IntegrationType), nullable=False)
    # TinyTuya: access_key + access_key_secret. Tapo: username + password. Unused fields are null.
    # access_key, access_key_secret, password are encrypted at rest (see EncryptedText).
    access_key: Mapped[str | None] = mapped_column(EncryptedText(), nullable=True)
    access_key_secret: Mapped[str | None] = mapped_column(EncryptedText(), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password: Mapped[str | None] = mapped_column(EncryptedText(), nullable=True)
    devices: Mapped[list["Device"]] = relationship(back_populates="integration")

    def __repr__(self) -> str:
        return f"Integration(id={self.id}, type={self.type})"


class Device(TimestampMixin, Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    integration_id: Mapped[int] = mapped_column(ForeignKey("integrations.id"), nullable=False)
    integration: Mapped["Integration"] = relationship(back_populates="devices")
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_known_ip: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    controllable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="devices")

    def __repr__(self) -> str:
        return f"Device(id={self.id}, name={self.name})"
