"""Exercise CRUD and media upload endpoints — Phase 1."""

import logging
import uuid
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.exercise import (
    EquipmentType,
    Exercise,
    ExerciseMedia,
    MediaType,
    MuscleGroup,
)
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseListResponse,
    ExerciseMediaOut,
    ExerciseOut,
    ExerciseUpdate,
    MediaTimestampUpdate,
)
from app.storage import generate_presigned_url, upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exercises", tags=["exercises"])


# ── Helpers ───────────────────────────────────────────────────────────────────


def _media_with_url(media: ExerciseMedia) -> ExerciseMediaOut:
    """Serialise an ExerciseMedia row and attach a presigned URL."""
    out = ExerciseMediaOut.model_validate(media)
    try:
        out.url = generate_presigned_url(media.storage_path)
    except Exception:
        logger.warning("Failed to generate presigned URL for %s", media.storage_path)
        out.url = None
    return out


def _guess_media_type(filename: str) -> MediaType:
    """Infer the MediaType enum from a file extension."""
    ext = PurePosixPath(filename).suffix.lower()
    if ext == ".gif":
        return MediaType.gif
    if ext in {".mp4", ".mov", ".webm", ".avi", ".mkv"}:
        return MediaType.video
    return MediaType.image


# ── LIST ──────────────────────────────────────────────────────────────────────


@router.get("", response_model=ExerciseListResponse)
async def list_exercises(
    primary_muscle: MuscleGroup | None = Query(None),
    equipment: EquipmentType | None = Query(None),
    q: str | None = Query(None, description="Search exercise name (case-insensitive)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Return a paginated, filterable list of exercises (without media)."""

    # -- base query --------------------------------------------------------
    query = select(Exercise)
    count_query = select(func.count()).select_from(Exercise)

    # -- filters -----------------------------------------------------------
    if primary_muscle is not None:
        query = query.where(Exercise.primary_muscle == primary_muscle)
        count_query = count_query.where(Exercise.primary_muscle == primary_muscle)
    if equipment is not None:
        query = query.where(Exercise.equipment == equipment)
        count_query = count_query.where(Exercise.equipment == equipment)
    if q:
        like_pattern = f"%{q}%"
        query = query.where(Exercise.name.ilike(like_pattern))
        count_query = count_query.where(Exercise.name.ilike(like_pattern))

    # -- total count -------------------------------------------------------
    total: int = (await db.execute(count_query)).scalar_one()

    # -- paginated rows ----------------------------------------------------
    offset = (page - 1) * page_size
    query = query.order_by(Exercise.name).offset(offset).limit(page_size)
    rows = (await db.execute(query)).scalars().all()

    # Return exercises without populating media presigned URLs (too expensive
    # for a list endpoint).  Media objects are still included via selectin
    # eager loading, but without the `url` field populated.
    return ExerciseListResponse(
        items=[ExerciseOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


# ── DETAIL ────────────────────────────────────────────────────────────────────


@router.get("/{exercise_id}", response_model=ExerciseOut)
async def get_exercise(
    exercise_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a single exercise with media (presigned URLs populated)."""

    stmt = select(Exercise).where(Exercise.id == exercise_id)
    exercise = (await db.execute(stmt)).scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    out = ExerciseOut.model_validate(exercise)
    # Replace media list with versions that have presigned URLs.
    out.media = [_media_with_url(m) for m in exercise.media]
    return out


# ── CREATE ────────────────────────────────────────────────────────────────────


@router.post("", response_model=ExerciseOut, status_code=201)
async def create_exercise(
    body: ExerciseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new exercise."""

    exercise = Exercise(
        name=body.name,
        description=body.description,
        instructions=body.instructions,
        primary_muscle=body.primary_muscle,
        secondary_muscles=[m.value for m in body.secondary_muscles],
        equipment=body.equipment,
        is_custom=body.is_custom,
    )
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return ExerciseOut.model_validate(exercise)


# ── UPDATE ────────────────────────────────────────────────────────────────────


@router.patch("/{exercise_id}", response_model=ExerciseOut)
async def update_exercise(
    exercise_id: str,
    body: ExerciseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update an exercise."""

    stmt = select(Exercise).where(Exercise.id == exercise_id)
    exercise = (await db.execute(stmt)).scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    updates = body.model_dump(exclude_unset=True)
    # Convert secondary_muscles enum values to plain strings for the ARRAY column.
    if "secondary_muscles" in updates and updates["secondary_muscles"] is not None:
        updates["secondary_muscles"] = [
            m.value if isinstance(m, MuscleGroup) else m
            for m in updates["secondary_muscles"]
        ]

    for field, value in updates.items():
        setattr(exercise, field, value)

    await db.commit()
    await db.refresh(exercise)
    return ExerciseOut.model_validate(exercise)


# ── MEDIA UPLOAD ──────────────────────────────────────────────────────────────


@router.post("/{exercise_id}/media", response_model=ExerciseMediaOut, status_code=201)
async def upload_media(
    exercise_id: str,
    file: UploadFile = File(...),
    media_type: str | None = Form(None),
    is_primary: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    """Upload a media file (image / gif / video) for an exercise."""

    # Ensure the exercise exists.
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    exercise = (await db.execute(stmt)).scalar_one_or_none()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Determine media type.
    if media_type:
        try:
            resolved_type = MediaType(media_type)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid media_type '{media_type}'. Must be one of: {[t.value for t in MediaType]}",
            )
    else:
        resolved_type = _guess_media_type(file.filename or "upload.bin")

    # Build the storage key.
    ext = PurePosixPath(file.filename or "upload.bin").suffix or ".bin"
    object_key = f"exercises/{exercise_id}/{uuid.uuid4()}{ext}"

    # Upload to MinIO.
    content_type = file.content_type or "application/octet-stream"
    upload_file(file.file, object_key, content_type)

    # Persist the media record.
    media = ExerciseMedia(
        exercise_id=exercise.id,
        media_type=resolved_type,
        storage_path=object_key,
        is_primary=is_primary,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)

    return _media_with_url(media)


# ── MEDIA TIMESTAMP UPDATE ────────────────────────────────────────────────────


@router.patch(
    "/{exercise_id}/media/{media_id}",
    response_model=ExerciseMediaOut,
)
async def update_media_timestamps(
    exercise_id: str,
    media_id: str,
    body: MediaTimestampUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update demo start/end timestamps on a media record."""

    stmt = (
        select(ExerciseMedia)
        .where(ExerciseMedia.id == media_id)
        .where(ExerciseMedia.exercise_id == exercise_id)
    )
    media = (await db.execute(stmt)).scalar_one_or_none()
    if media is None:
        raise HTTPException(status_code=404, detail="Media not found")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(media, field, value)

    await db.commit()
    await db.refresh(media)
    return _media_with_url(media)
