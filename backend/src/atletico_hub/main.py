from fastapi import Depends, FastAPI

from atletico_hub.auth.dependencies import require_csrf_header
from atletico_hub.auth.router import router as auth_router
from atletico_hub.players.profile_router import router as profile_router
from atletico_hub.players.router import router as players_router
from atletico_hub.settings import ApiSettings


def create_app(settings: ApiSettings) -> FastAPI:
    docs_url, redoc_url, openapi_url = ("/docs", "/redoc", "/openapi.json") if settings.docs_enabled else (None,) * 3
    app = FastAPI(
        title="Atletico Hub API",
        dependencies=[Depends(require_csrf_header)],
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    app.include_router(auth_router)
    app.include_router(players_router)
    app.include_router(profile_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app(ApiSettings())
