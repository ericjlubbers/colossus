from app.routers.exercises import router as exercises_router
from app.routers.templates import router as templates_router
from app.routers.workouts import router as workouts_router

__all__ = ["exercises_router", "templates_router", "workouts_router"]
