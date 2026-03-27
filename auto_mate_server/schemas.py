"""Pydantic schemas for API contracts."""

from typing import Self

from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str


class BootstrapResponse(BaseModel):
    is_setup: bool


class FirstUserSetupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=255)


class AuthResponse(BaseModel):
    user_id: int
    email: str
    is_admin: bool
    message: str
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str
    is_admin: bool

    model_config = {"from_attributes": True}


class UserCreateRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=255)
    is_admin: bool = False


class IntegrationOut(BaseModel):
    id: int
    user_id: int
    type: str
    username: str | None = None
    access_keys_configured: bool = False
    owner_email: str | None = None

    model_config = {"from_attributes": True}


class IntegrationCreateRequest(BaseModel):
    """TinyTuya: only access_key + access_key_secret. Tapo: only username + password."""

    type: str = Field(description="TINYTUYA or TAPO")
    access_key: str | None = Field(default=None, max_length=255)
    access_key_secret: str | None = Field(default=None, max_length=255)
    device_id: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    user_id: int | None = Field(
        default=None,
        description="Target user (admin only). Defaults to current user.",
    )

    @model_validator(mode="after")
    def validate_by_integration_type(self) -> Self:
        key = self.type.strip().upper()
        if key == "TINYTUYA":
            ak = (self.access_key or "").strip()
            aks = (self.access_key_secret or "").strip()
            if not ak or not aks:
                raise ValueError("TinyTuya requires access_key and access_key_secret")
            if (self.username or "").strip() != "" or (self.password or "").strip() != "":
                raise ValueError("TinyTuya must not include username or password")
        elif key == "TAPO":
            u = (self.username or "").strip()
            p = (self.password or "").strip()
            if not u or not p:
                raise ValueError("Tapo requires username and password")
            if (self.access_key or "").strip() != "" or (self.access_key_secret or "").strip() != "":
                raise ValueError("Tapo must not include access_key or access_key_secret")
        else:
            raise ValueError("type must be TINYTUYA or TAPO")
        return self


class DeviceOut(BaseModel):
    id: int
    integration_id: int
    user_id: int
    name: str
    last_known_ip: str
    payload: dict
    controllable: bool

    model_config = {"from_attributes": True}


class DeviceCreateRequest(BaseModel):
    integration_id: int
    name: str = Field(min_length=1, max_length=255)
    last_known_ip: str = Field(min_length=1, max_length=255)
    payload: dict = Field(default_factory=dict)
    controllable: bool = False

