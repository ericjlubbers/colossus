"""CompletedWorkout and CompletedSet ORM models — Phase 3."""

import uuid
from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CompletedWorkout(Base):
    __tablename__ = "completed_workouts"

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
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("workout_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    sets: Mapped[list["CompletedSet"]] = relationship(
        "CompletedSet",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="CompletedSet.set_number",
    )
    template: Mapped["WorkoutTemplate | None"] = relationship(  # type: ignore[name-defined]
        "WorkoutTemplate",
        foreign_keys=[template_id],
        lazy="select",
    )


class CompletedSet(Base):
    __tablename__ = "completed_sets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    workout_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("completed_workouts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    block_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("template_blocks.id", ondelete="SET NULL"),
        nullable=True,
    )
    set_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    reps_completed: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(precision=7, scale=2), nullable=True
    )
    is_warmup: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    is_failure: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false")
    )
    rpe: Mapped[Decimal | None] = mapped_column(
        sa.Numeric(precision=3, scale=1), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    workout: Mapped["CompletedWorkout"] = relationship(
        "CompletedWorkout", back_populates="sets"
    )
    exercise: Mapped["Exercise"] = relationship(  # type: ignore[name-defined]
        "Exercise", foreign_keys=[exercise_id], lazy="select"
    )
