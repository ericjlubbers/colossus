"""Pydantic v2 schemas for the Workout Template domain — Phase 2."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.template import BlockType


# ── Exercise summary (embedded in block exercise rows) ────────────────────────


class ExerciseSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    primary_muscle: str
    equipment: str


# ── Set definition (element of the JSONB sets array) ─────────────────────────


class TemplateSet(BaseModel):
    set_number: int
    target_reps_min: int | None = None
    target_reps_max: int | None = None
    target_weight: float | None = None
    weight_type: Literal["fixed", "pct_1rm", "auto"] = "fixed"
    is_warmup: bool = False
    notes: str | None = None


# ── TemplateBlockExercise ─────────────────────────────────────────────────────


class TemplateBlockExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    block_id: UUID
    exercise_id: UUID
    order_in_block: int
    sets: list[TemplateSet]
    progression_override: dict | None = None
    exercise: ExerciseSummaryOut | None = None


class TemplateBlockExerciseCreate(BaseModel):
    exercise_id: UUID
    order_in_block: int = 0
    sets: list[TemplateSet] = []
    progression_override: dict | None = None


class TemplateBlockExerciseUpdate(BaseModel):
    order_in_block: int | None = None
    sets: list[TemplateSet] | None = None
    progression_override: dict | None = None


class ExercisesReorderBody(BaseModel):
    items: list[dict]  # [{id: str, order_in_block: int}]


# ── TemplateBlock ─────────────────────────────────────────────────────────────


class TemplateBlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID
    block_type: BlockType
    order: int
    rest_after_seconds: int | None = None
    exercises: list[TemplateBlockExerciseOut] = []


class TemplateBlockCreate(BaseModel):
    block_type: BlockType = BlockType.set
    order: int
    rest_after_seconds: int | None = None


class TemplateBlockUpdate(BaseModel):
    block_type: BlockType | None = None
    order: int | None = None
    rest_after_seconds: int | None = None


class BlocksReorderBody(BaseModel):
    items: list[dict]  # [{id: str, order: int}]


# ── WorkoutTemplate ───────────────────────────────────────────────────────────


class TemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    name: str
    description: str | None = None
    estimated_duration_minutes: int | None = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime
    blocks: list[TemplateBlockOut] = []


class TemplateSummaryOut(BaseModel):
    """Lightweight template for list endpoints (no blocks)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    name: str
    description: str | None = None
    estimated_duration_minutes: int | None = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime


class TemplateListResponse(BaseModel):
    items: list[TemplateSummaryOut]
    total: int
    page: int
    page_size: int


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1)
    tags: list[str] = []


class TemplateUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1)
    tags: list[str] | None = None
