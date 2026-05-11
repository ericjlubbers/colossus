from fastapi import FastAPI

app = FastAPI(
    title="Colossus API",
    version="0.1.0",
    description="Self-hosted fitness tracking API",
)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Liveness probe — returns app identity and version."""
    return {
        "status": "ok",
        "app": "colossus",
        "version": "0.1.0",
    }
