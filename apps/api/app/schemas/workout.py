"""Pydantic v2 schemas for the Workout (session) domain — Phase 3."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ── CompletedSet ──────────────────────────────────────────────────────────────


class CompletedSetCreate(BaseModel):
    exercise_id: UUID
    block_id: UUID | None = None
    set_number: int = Field(..., ge=1)
    reps_completed: int | None = Field(None, ge=0)
    weight: Decimal | None = Field(None, ge=0)
    is_warmup: bool = False
    is_failure: bool = False
    rpe: Decimal | None = Field(None, ge=1, le=10)
    notes: str | None = None


class CompletedSetUpdate(BaseModel):
    reps_completed: int | None = Field(None, ge=0)
    weight: Decimal | None = Field(None, ge=0)
    is_warmup: bool | None = None
    is_failure: bool | None = None
    rpe: Decimal | None = Field(None, ge=1, le=10)
    notes: str | None = None


class ExerciseSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    primary_muscle: str
    equipment: str


class CompletedSetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workout_id: UUID
    exercise_id: UUID
    block_id: UUID | None
    set_number: int
    reps_completed: int | None
    weight: Decimal | None
    is_warmup: bool
    is_failure: bool
    rpe: Decimal | None
    notes: str | None
    logged_at: datetime
    exercise: ExerciseSummaryOut | None = None


# ── CompletedWorkout ──────────────────────────────────────────────────────────


class WorkoutStart(BaseModel):
    """Payload to start a new workout session."""
    template_id: UUID | None = None
    notes: str | None = None


class WorkoutUpdate(BaseModel):
    notes: str | None = None
    ended_at: datetime | None = None


class TemplateSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class CompletedWorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None
    template_id: UUID | None
    notes: str | None
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    sets: list[CompletedSetOut] = []
    template: TemplateSummaryOut | None = None
