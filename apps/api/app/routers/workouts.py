"""Workout session endpoints — Phase 3.

Routes:
  POST   /workouts                     — start a session
  GET    /workouts/{workout_id}        — fetch session detail
  PATCH  /workouts/{workout_id}        — update notes / ended_at
  POST   /workouts/{workout_id}/finish — mark complete
  POST   /workouts/{workout_id}/sets   — log a completed set
  PATCH  /workouts/{workout_id}/sets/{set_id}  — edit a set
  DELETE /workouts/{workout_id}/sets/{set_id}  — remove a set
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.workout import CompletedSet, CompletedWorkout
from app.models.exercise import Exercise
from app.schemas.workout import (
    CompletedSetCreate,
    CompletedSetOut,
    CompletedSetUpdate,
    CompletedWorkoutOut,
    WorkoutStart,
    WorkoutUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workouts", tags=["workouts"])

# ── Load options ──────────────────────────────────────────────────────────────

_FULL_WORKOUT_OPTIONS = [
    selectinload(CompletedWorkout.sets).selectinload(CompletedSet.exercise),
    selectinload(CompletedWorkout.template),
]


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _get_workout_or_404(
    workout_id: str,
    db: AsyncSession,
    *,
    with_sets: bool = False,
) -> CompletedWorkout:
    stmt = select(CompletedWorkout).where(CompletedWorkout.id == workout_id)
    if with_sets:
        stmt = stmt.options(*_FULL_WORKOUT_OPTIONS)
    result = await db.execute(stmt)
    workout = result.scalar_one_or_none()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


async def _get_set_or_404(
    set_id: str,
    workout_id: str,
    db: AsyncSession,
) -> CompletedSet:
    stmt = select(CompletedSet).where(
        CompletedSet.id == set_id,
        CompletedSet.workout_id == workout_id,
    )
    result = await db.execute(stmt)
    completed_set = result.scalar_one_or_none()
    if completed_set is None:
        raise HTTPException(status_code=404, detail="Set not found")
    return completed_set


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("", response_model=CompletedWorkoutOut, status_code=201)
async def start_workout(
    body: WorkoutStart,
    db: AsyncSession = Depends(get_db),
) -> CompletedWorkout:
    """Start a new workout session (optionally from a template)."""
    workout = CompletedWorkout(
        id=uuid.uuid4(),
        template_id=body.template_id,
        notes=body.notes,
        started_at=datetime.now(timezone.utc),
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)

    # Reload with relations for serialisation
    result = await db.execute(
        select(CompletedWorkout)
        .where(CompletedWorkout.id == workout.id)
        .options(*_FULL_WORKOUT_OPTIONS)
    )
    return result.scalar_one()


@router.get("/{workout_id}", response_model=CompletedWorkoutOut)
async def get_workout(
    workout_id: str,
    db: AsyncSession = Depends(get_db),
) -> CompletedWorkout:
    return await _get_workout_or_404(workout_id, db, with_sets=True)


@router.patch("/{workout_id}", response_model=CompletedWorkoutOut)
async def update_workout(
    workout_id: str,
    body: WorkoutUpdate,
    db: AsyncSession = Depends(get_db),
) -> CompletedWorkout:
    workout = await _get_workout_or_404(workout_id, db)
    if body.notes is not None:
        workout.notes = body.notes
    if body.ended_at is not None:
        workout.ended_at = body.ended_at
    await db.commit()
    return await _get_workout_or_404(workout_id, db, with_sets=True)


@router.post("/{workout_id}/finish", response_model=CompletedWorkoutOut)
async def finish_workout(
    workout_id: str,
    db: AsyncSession = Depends(get_db),
) -> CompletedWorkout:
    """Mark a workout session as complete (sets ended_at to now if not already set)."""
    workout = await _get_workout_or_404(workout_id, db)
    if workout.ended_at is None:
        workout.ended_at = datetime.now(timezone.utc)
    await db.commit()
    return await _get_workout_or_404(workout_id, db, with_sets=True)


@router.post("/{workout_id}/sets", response_model=CompletedSetOut, status_code=201)
async def log_set(
    workout_id: str,
    body: CompletedSetCreate,
    db: AsyncSession = Depends(get_db),
) -> CompletedSet:
    """Log a completed set within a workout session."""
    # Verify workout exists
    await _get_workout_or_404(workout_id, db)

    # Verify exercise exists
    ex_result = await db.execute(
        select(Exercise).where(Exercise.id == body.exercise_id)
    )
    if ex_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    completed_set = CompletedSet(
        id=uuid.uuid4(),
        workout_id=uuid.UUID(workout_id),
        exercise_id=body.exercise_id,
        block_id=body.block_id,
        set_number=body.set_number,
        reps_completed=body.reps_completed,
        weight=body.weight,
        is_warmup=body.is_warmup,
        is_failure=body.is_failure,
        rpe=body.rpe,
        notes=body.notes,
        logged_at=datetime.now(timezone.utc),
    )
    db.add(completed_set)
    await db.commit()
    await db.refresh(completed_set)

    # Reload with exercise relation
    result = await db.execute(
        select(CompletedSet)
        .where(CompletedSet.id == completed_set.id)
        .options(selectinload(CompletedSet.exercise))
    )
    return result.scalar_one()


@router.patch(
    "/{workout_id}/sets/{set_id}", response_model=CompletedSetOut
)
async def update_set(
    workout_id: str,
    set_id: str,
    body: CompletedSetUpdate,
    db: AsyncSession = Depends(get_db),
) -> CompletedSet:
    completed_set = await _get_set_or_404(set_id, workout_id, db)
    if body.reps_completed is not None:
        completed_set.reps_completed = body.reps_completed
    if body.weight is not None:
        completed_set.weight = body.weight
    if body.is_warmup is not None:
        completed_set.is_warmup = body.is_warmup
    if body.is_failure is not None:
        completed_set.is_failure = body.is_failure
    if body.rpe is not None:
        completed_set.rpe = body.rpe
    if body.notes is not None:
        completed_set.notes = body.notes
    await db.commit()

    result = await db.execute(
        select(CompletedSet)
        .where(CompletedSet.id == completed_set.id)
        .options(selectinload(CompletedSet.exercise))
    )
    return result.scalar_one()


@router.delete("/{workout_id}/sets/{set_id}", status_code=204)
async def delete_set(
    workout_id: str,
    set_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    completed_set = await _get_set_or_404(set_id, workout_id, db)
    await db.delete(completed_set)
    await db.commit()
