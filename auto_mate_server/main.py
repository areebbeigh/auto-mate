"""FastAPI app entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auto_mate_server.config import settings
from auto_mate_server.db.models import Base
from auto_mate_server.db.session import engine
from auto_mate_server.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    def startup() -> None:
        # Keep local/dev setup simple by ensuring tables exist.
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "auto_mate_server.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )


if __name__ == "__main__":
    run()

