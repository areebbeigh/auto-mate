"""API route definitions."""

from typing import Annotated
from datetime import datetime

import jwt  # type: ignore[import-not-found]
from fastapi import APIRouter, Depends, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from auto_mate_server.config import settings
from common.enums import IntegrationType

from auto_mate_server.db.models import Device, Integration, User
from auto_mate_server.db.session import get_db
from auto_mate_server.integration_validation import integration_credentials_for_db
from auto_mate_server.schemas import (
    AuthResponse,
    BootstrapResponse,
    DeviceCreateRequest,
    DeviceOut,
    FirstUserSetupRequest,
    HealthResponse,
    IntegrationCreateRequest,
    IntegrationOut,
    LoginRequest,
    UserCreateRequest,
    UserOut,
)
from auto_mate_server.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from common.service.mqtt import get_mqtt_service, MQTTService
from common.dto.event.integration import IntegrationCreate
from common.dto.topics import AgentTopics

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


@router.get("/test-mqtt")
def test(mqtt_service: MQTTService = Depends(get_mqtt_service)):
    if settings.APP_ENV == "dev":
        event = IntegrationCreate(id=1, type=IntegrationType.TINYTUYA, access_key="1234567890", access_key_secret="1234567890", username="test", password="test", created_at=datetime.now()).model_dump_json()
        mqtt_service.publish(AgentTopics.INTEGRATION_CREATE.topic, event)
        return {"message": "Message published"}
    raise HTTPException(status_code=404)

@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        environment=settings.APP_ENV,
    )


def _issue_auth_response(user: User, message: str) -> AuthResponse:
    token = create_access_token(subject=str(user.id))
    return AuthResponse(
        user_id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        message=message,
        access_token=token,
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token.")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.") from exc

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.") from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user


def _parse_integration_type(value: str) -> IntegrationType:
    key = value.strip().upper()
    try:
        return IntegrationType[key]
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid integration type: {value}. Expected TINYTUYA or TAPO.",
        ) from exc


@router.get("/bootstrap", response_model=BootstrapResponse, tags=["auth"])
def bootstrap(db: Session = Depends(get_db)) -> BootstrapResponse:
    first_user = db.scalar(select(User.id).limit(1))
    return BootstrapResponse(is_setup=first_user is not None)


@router.post(
    "/auth/setup-first-user",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
def setup_first_user(payload: FirstUserSetupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    first_user = db.scalar(select(User.id).limit(1))
    if first_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="First user is already configured.",
        )

    user = User(
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _issue_auth_response(user=user, message="First user created successfully.")


@router.post("/auth/login", response_model=AuthResponse, tags=["auth"])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower().strip()).limit(1))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return _issue_auth_response(user=user, message="Login successful.")


@router.get("/auth/me", response_model=AuthResponse, tags=["auth"])
def get_me(current_user: User = Depends(get_current_user)) -> AuthResponse:
    return _issue_auth_response(user=current_user, message="Session is valid.")


def _integration_to_out(row: Integration, owner_email: str | None = None) -> IntegrationOut:
    ak = (row.access_key or "").strip()
    aks = (row.access_key_secret or "").strip()
    return IntegrationOut(
        id=row.id,
        user_id=row.user_id,
        type=row.type.value if hasattr(row.type, "value") else str(row.type),
        username=row.username,
        access_keys_configured=bool(ak and aks),
        owner_email=owner_email,
    )


def _ensure_integration_visible(current_user: User, row: Integration) -> None:
    if current_user.is_admin:
        return
    if row.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this integration.",
        )


@router.get("/integrations", response_model=list[IntegrationOut], tags=["integrations"])
def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IntegrationOut]:
    q = select(Integration).options(joinedload(Integration.user)).order_by(Integration.id)
    if not current_user.is_admin:
        q = q.where(Integration.user_id == current_user.id)
    rows = db.scalars(q).unique().all()
    out: list[IntegrationOut] = []
    for r in rows:
        owner_email = r.user.email if getattr(r, "user", None) is not None else None
        out.append(_integration_to_out(r, owner_email=owner_email))
    return out


@router.post(
    "/integrations",
    response_model=IntegrationOut,
    status_code=status.HTTP_201_CREATED,
    tags=["integrations"],
)
def create_integration(
    payload: IntegrationCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> IntegrationOut:
    target_user_id = payload.user_id if payload.user_id is not None else admin.id
    if payload.user_id is not None:
        target = db.get(User, payload.user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    itype = _parse_integration_type(payload.type)
    creds = integration_credentials_for_db(itype, payload)
    row = Integration(
        user_id=target_user_id,
        type=itype,
        **creds,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    owner = db.get(User, row.user_id)
    return _integration_to_out(row, owner_email=owner.email if owner else None)


@router.get("/integrations/{integration_id}", response_model=IntegrationOut, tags=["integrations"])
def get_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntegrationOut:
    row = db.get(Integration, integration_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")
    _ensure_integration_visible(current_user, row)
    owner = db.get(User, row.user_id)
    return _integration_to_out(row, owner_email=owner.email if owner else None)


@router.put("/integrations/{integration_id}", response_model=IntegrationOut, tags=["integrations"])
def update_integration(
    integration_id: int,
    payload: IntegrationCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> IntegrationOut:
    row = db.get(Integration, integration_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")

    itype = _parse_integration_type(payload.type)
    creds = integration_credentials_for_db(itype, payload)

    target_user_id = row.user_id
    if payload.user_id is not None:
        target = db.get(User, payload.user_id)
        if target is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        target_user_id = payload.user_id

    row.user_id = target_user_id
    row.type = itype
    row.access_key = creds["access_key"]
    row.access_key_secret = creds["access_key_secret"]
    row.username = creds["username"]
    row.password = creds["password"]
    db.commit()
    db.refresh(row)
    owner = db.get(User, row.user_id)
    return _integration_to_out(row, owner_email=owner.email if owner else None)


@router.delete(
    "/integrations/{integration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["integrations"],
)
def delete_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> None:
    row = db.get(Integration, integration_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")
    db.execute(delete(Device).where(Device.integration_id == integration_id))
    db.delete(row)
    db.commit()


@router.get("/devices", response_model=list[DeviceOut], tags=["devices"])
def list_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DeviceOut]:
    if current_user.is_admin:
        rows = db.scalars(select(Device).order_by(Device.id)).all()
    else:
        rows = db.scalars(
            select(Device).where(Device.user_id == current_user.id).order_by(Device.id)
        ).all()
    return [DeviceOut.model_validate(r) for r in rows]


@router.post(
    "/devices",
    response_model=DeviceOut,
    status_code=status.HTTP_201_CREATED,
    tags=["devices"],
)
def create_device(
    payload: DeviceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DeviceOut:
    integration = db.get(Integration, payload.integration_id)
    if integration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")
    if not current_user.is_admin and integration.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed for this integration.")

    row = Device(
        integration_id=payload.integration_id,
        user_id=integration.user_id,
        name=payload.name,
        last_known_ip=payload.last_known_ip,
        payload=payload.payload,
        controllable=payload.controllable,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return DeviceOut.model_validate(row)


@router.get("/users", response_model=list[UserOut], tags=["users"])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> list[UserOut]:
    rows = db.scalars(select(User).order_by(User.id)).all()
    return [UserOut.model_validate(r) for r in rows]


@router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
) -> UserOut:
    email = payload.email.lower().strip()
    existing = db.scalar(select(User).where(User.email == email).limit(1))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

