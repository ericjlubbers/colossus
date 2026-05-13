"""WorkoutTemplate, TemplateBlock, TemplateBlockExercise ORM models — Phase 2."""

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.exercise import Exercise  # noqa: F401 — needed for the TBE relationship


# ── Enums ─────────────────────────────────────────────────────────────────────


class BlockType(str, enum.Enum):
    set = "set"
    superset = "superset"


# ── WorkoutTemplate ───────────────────────────────────────────────────────────


class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(
        sa.Integer, nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(sa.String()),
        nullable=False,
        server_default=sa.text("'{}'"),
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    blocks: Mapped[list["TemplateBlock"]] = relationship(
        "TemplateBlock",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="TemplateBlock.order",
    )


# ── TemplateBlock ─────────────────────────────────────────────────────────────


class TemplateBlock(Base):
    __tablename__ = "template_blocks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("workout_templates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    block_type: Mapped[BlockType] = mapped_column(
        sa.Enum(
            BlockType, name="blocktype", create_constraint=False, native_enum=True
        ),
        nullable=False,
    )
    order: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    rest_after_seconds: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)

    template: Mapped["WorkoutTemplate"] = relationship(
        "WorkoutTemplate", back_populates="blocks"
    )
    exercises: Mapped[list["TemplateBlockExercise"]] = relationship(
        "TemplateBlockExercise",
        back_populates="block",
        cascade="all, delete-orphan",
        order_by="TemplateBlockExercise.order_in_block",
    )


# ── TemplateBlockExercise ─────────────────────────────────────────────────────


class TemplateBlockExercise(Base):
    __tablename__ = "template_block_exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    block_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("template_blocks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_in_block: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default=sa.text("0")
    )
    sets: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")
    )
    progression_override: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    block: Mapped["TemplateBlock"] = relationship(
        "TemplateBlock", back_populates="exercises"
    )
    exercise: Mapped["Exercise"] = relationship("Exercise", lazy="joined")
