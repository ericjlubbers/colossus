"""Exercise and ExerciseMedia ORM models — Phase 1 (Exercise Library)."""

import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ── Enums ─────────────────────────────────────────────────────────────────────


class MuscleGroup(str, enum.Enum):
    chest = "chest"
    back = "back"
    shoulders = "shoulders"
    biceps = "biceps"
    triceps = "triceps"
    forearms = "forearms"
    core = "core"
    quads = "quads"
    hamstrings = "hamstrings"
    glutes = "glutes"
    calves = "calves"


class EquipmentType(str, enum.Enum):
    barbell = "barbell"
    dumbbell = "dumbbell"
    cable = "cable"
    machine = "machine"
    bodyweight = "bodyweight"
    kettlebell = "kettlebell"
    band = "band"
    other = "other"


class MediaType(str, enum.Enum):
    gif = "gif"
    video = "video"
    image = "image"


# ── Exercise ──────────────────────────────────────────────────────────────────


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        sa.Text,
        nullable=True,
    )
    instructions: Mapped[str | None] = mapped_column(
        sa.Text,
        nullable=True,
    )
    primary_muscle: Mapped[MuscleGroup] = mapped_column(
        sa.Enum(
            MuscleGroup, name="musclegroup", create_constraint=False, native_enum=True
        ),
        nullable=False,
        index=True,
    )
    secondary_muscles: Mapped[list[str]] = mapped_column(
        ARRAY(sa.String()),
        nullable=False,
        server_default="{}",
    )
    equipment: Mapped[EquipmentType] = mapped_column(
        sa.Enum(
            EquipmentType,
            name="equipmenttype",
            create_constraint=False,
            native_enum=True,
        ),
        nullable=False,
        index=True,
    )
    is_custom: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=sa.text("false"),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
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

    # ── Relationships ─────────────────────────────────────────────────────────
    media: Mapped[list["ExerciseMedia"]] = relationship(
        "ExerciseMedia",
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Exercise {self.name!r} ({self.primary_muscle.value})>"


# ── ExerciseMedia ─────────────────────────────────────────────────────────────


class ExerciseMedia(Base):
    __tablename__ = "exercise_media"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=sa.text("gen_random_uuid()"),
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    media_type: Mapped[MediaType] = mapped_column(
        sa.Enum(MediaType, name="mediatype", create_constraint=False, native_enum=True),
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        sa.String(512),
        nullable=False,
    )
    source_url: Mapped[str | None] = mapped_column(
        sa.String(1024),
        nullable=True,
    )
    is_primary: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=sa.text("false"),
    )
    demo_start_seconds: Mapped[float | None] = mapped_column(
        sa.Float,
        nullable=True,
    )
    demo_end_seconds: Mapped[float | None] = mapped_column(
        sa.Float,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    exercise: Mapped["Exercise"] = relationship(
        "Exercise",
        back_populates="media",
    )

    def __repr__(self) -> str:
        return (
            f"<ExerciseMedia {self.media_type.value} for exercise={self.exercise_id}>"
        )
