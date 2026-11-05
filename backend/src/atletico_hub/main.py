from fastapi import FastAPI

app = FastAPI(title="Atletico Hub API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
