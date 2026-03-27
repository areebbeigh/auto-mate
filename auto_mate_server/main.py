"""FastAPI app entrypoint."""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from auto_mate_server.config import settings
from auto_mate_server.db.models import Base
from auto_mate_server.db.session import engine
from auto_mate_server.routes import router
from auto_mate_server.factory import get_mqtt_service
from auto_mate_server.mqtt_handler import MQTTRequestHandler
from common.service.mqtt import get_mqtt_service_ctx


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Keep local/dev setup simple by ensuring tables exist.
    Base.metadata.create_all(bind=engine)
    with get_mqtt_service_ctx("fast-api-rpc") as mqtt_service:
        mqtt_handler = MQTTRequestHandler(mqtt_service)
        mqtt_handler._subscribe_topics()
        yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()


def run() -> None:
    import uvicorn

    if not os.path.exists(settings.CONFIG_DIR):
        logger.info("Creating config dir")
        os.makedirs(settings.CONFIG_DIR)

    uvicorn.run(
        "auto_mate_server.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )


if __name__ == "__main__":
    run()

