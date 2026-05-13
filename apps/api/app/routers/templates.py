"""Workout template CRUD endpoints — Phase 2.

Route ordering note: /blocks/reorder must be registered BEFORE /blocks/{block_id},
and /exercises/reorder before /exercises/{tbe_id}, so FastAPI matches the literal
segment first rather than capturing "reorder" as a path parameter.
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.template import BlockType, TemplateBlock, TemplateBlockExercise, WorkoutTemplate
from app.schemas.template import (
    BlocksReorderBody,
    ExercisesReorderBody,
    TemplateBlockCreate,
    TemplateBlockExerciseCreate,
    TemplateBlockExerciseOut,
    TemplateBlockExerciseUpdate,
    TemplateBlockOut,
    TemplateBlockUpdate,
    TemplateCreate,
    TemplateListResponse,
    TemplateOut,
    TemplateSummaryOut,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


# ── Load helpers ──────────────────────────────────────────────────────────────

_FULL_TEMPLATE_OPTIONS = [
    selectinload(WorkoutTemplate.blocks).selectinload(
        TemplateBlock.exercises
    ).selectinload(TemplateBlockExercise.exercise)
]

_BLOCK_WITH_EXERCISES_OPTIONS = [
    selectinload(TemplateBlock.exercises).selectinload(TemplateBlockExercise.exercise)
]


async def _get_template_or_404(
    template_id: str,
    db: AsyncSession,
    *,
    with_blocks: bool = False,
) -> WorkoutTemplate:
    stmt = select(WorkoutTemplate).where(WorkoutTemplate.id == template_id)
    if with_blocks:
        stmt = stmt.options(*_FULL_TEMPLATE_OPTIONS)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


async def _get_block_or_404(
    block_id: str,
    template_id: str,
    db: AsyncSession,
    *,
    with_exercises: bool = False,
) -> TemplateBlock:
    stmt = select(TemplateBlock).where(
        TemplateBlock.id == block_id,
        TemplateBlock.template_id == template_id,
    )
    if with_exercises:
        stmt = stmt.options(*_BLOCK_WITH_EXERCISES_OPTIONS)
    block = (await db.execute(stmt)).scalar_one_or_none()
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return block


async def _get_tbe_or_404(
    tbe_id: str,
    block_id: str,
    db: AsyncSession,
) -> TemplateBlockExercise:
    stmt = select(TemplateBlockExercise).where(
        TemplateBlockExercise.id == tbe_id,
        TemplateBlockExercise.block_id == block_id,
    )
    tbe = (await db.execute(stmt)).scalar_one_or_none()
    if tbe is None:
        raise HTTPException(status_code=404, detail="Block exercise not found")
    return tbe


async def _reload_template(template_id: uuid.UUID, db: AsyncSession) -> WorkoutTemplate:
    stmt = (
        select(WorkoutTemplate)
        .where(WorkoutTemplate.id == template_id)
        .options(*_FULL_TEMPLATE_OPTIONS)
    )
    return (await db.execute(stmt)).scalar_one()


async def _reload_block(block_id: uuid.UUID, db: AsyncSession) -> TemplateBlock:
    stmt = (
        select(TemplateBlock)
        .where(TemplateBlock.id == block_id)
        .options(*_BLOCK_WITH_EXERCISES_OPTIONS)
    )
    return (await db.execute(stmt)).scalar_one()


# ── TEMPLATES ─────────────────────────────────────────────────────────────────


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    q: str | None = Query(None, description="Search by name (case-insensitive)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Return a paginated list of templates (no block detail)."""
    base = select(WorkoutTemplate)
    count_base = select(func.count()).select_from(WorkoutTemplate)

    if q:
        pattern = f"%{q}%"
        base = base.where(WorkoutTemplate.name.ilike(pattern))
        count_base = count_base.where(WorkoutTemplate.name.ilike(pattern))

    total: int = (await db.execute(count_base)).scalar_one()
    offset = (page - 1) * page_size
    rows = (
        await db.execute(
            base.order_by(WorkoutTemplate.updated_at.desc()).offset(offset).limit(page_size)
        )
    ).scalars().all()

    return TemplateListResponse(
        items=[TemplateSummaryOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=TemplateOut, status_code=201)
async def create_template(
    body: TemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new workout template."""
    template = WorkoutTemplate(
        name=body.name,
        description=body.description,
        estimated_duration_minutes=body.estimated_duration_minutes,
        tags=body.tags,
    )
    db.add(template)
    await db.commit()
    template = await _reload_template(template.id, db)
    return TemplateOut.model_validate(template)


@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return a template with all blocks and exercises."""
    template = await _get_template_or_404(template_id, db, with_blocks=True)
    return TemplateOut.model_validate(template)


@router.patch("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: str,
    body: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update template metadata (name, description, duration, tags)."""
    template = await _get_template_or_404(template_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    template.updated_at = datetime.now(timezone.utc)
    await db.commit()
    template = await _reload_template(template.id, db)
    return TemplateOut.model_validate(template)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a template and cascade to all blocks and exercises."""
    template = await _get_template_or_404(template_id, db)
    await db.delete(template)
    await db.commit()


# ── BLOCKS ────────────────────────────────────────────────────────────────────


@router.post("/{template_id}/blocks", response_model=TemplateBlockOut, status_code=201)
async def add_block(
    template_id: str,
    body: TemplateBlockCreate,
    db: AsyncSession = Depends(get_db),
):
    """Append a new block to a template."""
    await _get_template_or_404(template_id, db)
    block = TemplateBlock(
        template_id=uuid.UUID(template_id),
        block_type=body.block_type,
        order=body.order,
        rest_after_seconds=body.rest_after_seconds,
    )
    db.add(block)
    await db.commit()
    block = await _reload_block(block.id, db)
    return TemplateBlockOut.model_validate(block)


# NOTE: registered BEFORE /{block_id} so "reorder" is not captured as block_id
@router.patch("/{template_id}/blocks/reorder", response_model=TemplateOut)
async def reorder_blocks(
    template_id: str,
    body: BlocksReorderBody,
    db: AsyncSession = Depends(get_db),
):
    """Batch-update block ordering. Body: {"items": [{"id": "...", "order": 0}, ...]}"""
    template = await _get_template_or_404(template_id, db)
    order_map = {item["id"]: item["order"] for item in body.items}

    stmt = select(TemplateBlock).where(TemplateBlock.template_id == template.id)
    blocks = (await db.execute(stmt)).scalars().all()
    for block in blocks:
        new_order = order_map.get(str(block.id))
        if new_order is not None:
            block.order = new_order

    template.updated_at = datetime.now(timezone.utc)
    await db.commit()
    template = await _reload_template(template.id, db)
    return TemplateOut.model_validate(template)


@router.patch("/{template_id}/blocks/{block_id}", response_model=TemplateBlockOut)
async def update_block(
    template_id: str,
    block_id: str,
    body: TemplateBlockUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update block type, order, or rest timer."""
    block = await _get_block_or_404(block_id, template_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(block, field, value)
    await db.commit()
    block = await _reload_block(block.id, db)
    return TemplateBlockOut.model_validate(block)


@router.delete("/{template_id}/blocks/{block_id}", status_code=204)
async def delete_block(
    template_id: str,
    block_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a block and all its exercises."""
    block = await _get_block_or_404(block_id, template_id, db)
    await db.delete(block)
    await db.commit()


# ── BLOCK EXERCISES ───────────────────────────────────────────────────────────


@router.post(
    "/{template_id}/blocks/{block_id}/exercises",
    response_model=TemplateBlockExerciseOut,
    status_code=201,
)
async def add_exercise_to_block(
    template_id: str,
    block_id: str,
    body: TemplateBlockExerciseCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add an exercise slot to a block."""
    await _get_block_or_404(block_id, template_id, db)
    tbe = TemplateBlockExercise(
        block_id=uuid.UUID(block_id),
        exercise_id=body.exercise_id,
        order_in_block=body.order_in_block,
        sets=[s.model_dump() for s in body.sets],
        progression_override=body.progression_override,
    )
    db.add(tbe)
    await db.commit()
    # Reload with exercise join for name/details
    stmt = (
        select(TemplateBlockExercise)
        .where(TemplateBlockExercise.id == tbe.id)
        .options(selectinload(TemplateBlockExercise.exercise))
    )
    tbe = (await db.execute(stmt)).scalar_one()
    return TemplateBlockExerciseOut.model_validate(tbe)


# NOTE: registered BEFORE /{tbe_id} so "reorder" is not captured as tbe_id
@router.patch(
    "/{template_id}/blocks/{block_id}/exercises/reorder",
    response_model=TemplateBlockOut,
)
async def reorder_exercises(
    template_id: str,
    block_id: str,
    body: ExercisesReorderBody,
    db: AsyncSession = Depends(get_db),
):
    """Batch-update exercise ordering within a block.
    Body: {"items": [{"id": "...", "order_in_block": 0}, ...]}
    """
    block = await _get_block_or_404(block_id, template_id, db, with_exercises=True)
    order_map = {item["id"]: item["order_in_block"] for item in body.items}
    for tbe in block.exercises:
        new_order = order_map.get(str(tbe.id))
        if new_order is not None:
            tbe.order_in_block = new_order
    await db.commit()
    block = await _reload_block(block.id, db)
    return TemplateBlockOut.model_validate(block)


@router.patch(
    "/{template_id}/blocks/{block_id}/exercises/{tbe_id}",
    response_model=TemplateBlockExerciseOut,
)
async def update_block_exercise(
    template_id: str,
    block_id: str,
    tbe_id: str,
    body: TemplateBlockExerciseUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update sets, order, or progression override for an exercise in a block."""
    await _get_block_or_404(block_id, template_id, db)
    tbe = await _get_tbe_or_404(tbe_id, block_id, db)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(tbe, field, value)
    await db.commit()
    stmt = (
        select(TemplateBlockExercise)
        .where(TemplateBlockExercise.id == tbe.id)
        .options(selectinload(TemplateBlockExercise.exercise))
    )
    tbe = (await db.execute(stmt)).scalar_one()
    return TemplateBlockExerciseOut.model_validate(tbe)


@router.delete(
    "/{template_id}/blocks/{block_id}/exercises/{tbe_id}",
    status_code=204,
)
async def delete_block_exercise(
    template_id: str,
    block_id: str,
    tbe_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove an exercise from a block."""
    await _get_block_or_404(block_id, template_id, db)
    tbe = await _get_tbe_or_404(tbe_id, block_id, db)
    await db.delete(tbe)
    await db.commit()
