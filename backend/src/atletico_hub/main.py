from fastapi import Depends, FastAPI

from atletico_hub.auth.dependencies import require_csrf_header

app = FastAPI(title="Atletico Hub API", dependencies=[Depends(require_csrf_header)])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
