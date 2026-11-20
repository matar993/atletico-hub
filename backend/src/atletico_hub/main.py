from fastapi import Depends, FastAPI

from atletico_hub.auth.dependencies import require_csrf_header
from atletico_hub.auth.router import router as auth_router

app = FastAPI(title="Atletico Hub API", dependencies=[Depends(require_csrf_header)])

app.include_router(auth_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
