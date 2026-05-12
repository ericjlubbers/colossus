"""Pydantic v2 schemas for the Exercise domain — Phase 1."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.exercise import EquipmentType, MuscleGroup

# ── Media ─────────────────────────────────────────────────────────────────────


class ExerciseMediaOut(BaseModel):
    """Read-only representation of an exercise media asset."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    exercise_id: str
    media_type: str
    storage_path: str
    source_url: str | None = None
    is_primary: bool
    demo_start_seconds: float | None = None
    demo_end_seconds: float | None = None
    url: str | None = None  # Presigned URL — populated by the router
    created_at: datetime


class MediaTimestampUpdate(BaseModel):
    """Body for updating media demo timestamps."""

    demo_start_seconds: float | None = None
    demo_end_seconds: float | None = None


# ── Exercise ──────────────────────────────────────────────────────────────────


class ExerciseOut(BaseModel):
    """Read-only representation of an exercise."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    instructions: str | None = None
    primary_muscle: str
    secondary_muscles: list[str] = []
    equipment: str
    is_custom: bool
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime
    media: list[ExerciseMediaOut] = []


class ExerciseCreate(BaseModel):
    """Body for creating a new exercise."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    instructions: str | None = None
    primary_muscle: MuscleGroup
    secondary_muscles: list[MuscleGroup] = []
    equipment: EquipmentType
    is_custom: bool = True


class ExerciseUpdate(BaseModel):
    """Body for partially updating an exercise."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    instructions: str | None = None
    primary_muscle: MuscleGroup | None = None
    secondary_muscles: list[MuscleGroup] | None = None
    equipment: EquipmentType | None = None


class ExerciseListResponse(BaseModel):
    """Paginated list of exercises."""

    items: list[ExerciseOut]
    total: int
    page: int
    page_size: int
