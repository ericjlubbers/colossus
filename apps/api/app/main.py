from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import exercises_router, templates_router, workouts_router

app = FastAPI(
    title="Colossus API",
    version="0.1.0",
    description="Self-hosted fitness tracking API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercises_router)
app.include_router(templates_router)
app.include_router(workouts_router)


@app.get("/health", tags=["meta"])
async def health() -> dict:
    """Liveness probe — returns app identity and version."""
    return {
        "status": "ok",
        "app": "colossus",
        "version": "0.1.0",
    }
