"""Create exercise tables.

Revision ID: 0001
Revises: (none — initial migration)
Create Date: 2025-06-14
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# ── Enum definitions ──────────────────────────────────────────────────────────
musclegroup_enum = postgresql.ENUM(
    "chest",
    "back",
    "shoulders",
    "biceps",
    "triceps",
    "forearms",
    "core",
    "quads",
    "hamstrings",
    "glutes",
    "calves",
    name="musclegroup",
    create_type=False,
)

equipmenttype_enum = postgresql.ENUM(
    "barbell",
    "dumbbell",
    "cable",
    "machine",
    "bodyweight",
    "kettlebell",
    "band",
    "other",
    name="equipmenttype",
    create_type=False,
)

mediatype_enum = postgresql.ENUM(
    "gif",
    "video",
    "image",
    name="mediatype",
    create_type=False,
)


def upgrade() -> None:
    # 1. Create enum types
    musclegroup_enum.create(op.get_bind(), checkfirst=True)
    equipmenttype_enum.create(op.get_bind(), checkfirst=True)
    mediatype_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create exercises table
    op.create_table(
        "exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column(
            "primary_muscle",
            musclegroup_enum,
            nullable=False,
        ),
        sa.Column(
            "secondary_muscles",
            postgresql.ARRAY(sa.String()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "equipment",
            equipmenttype_enum,
            nullable=False,
        ),
        sa.Column(
            "is_custom",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Create indexes on exercises
    op.create_index("ix_exercises_name", "exercises", ["name"])
    op.create_index("ix_exercises_primary_muscle", "exercises", ["primary_muscle"])
    op.create_index("ix_exercises_equipment", "exercises", ["equipment"])

    # 4. Create exercise_media table
    op.create_table(
        "exercise_media",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "exercise_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "media_type",
            mediatype_enum,
            nullable=False,
        ),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("demo_start_seconds", sa.Float(), nullable=True),
        sa.Column("demo_end_seconds", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            ondelete="CASCADE",
        ),
    )


def downgrade() -> None:
    op.drop_table("exercise_media")
    op.drop_table("exercises")

    mediatype_enum.drop(op.get_bind(), checkfirst=True)
    equipmenttype_enum.drop(op.get_bind(), checkfirst=True)
    musclegroup_enum.drop(op.get_bind(), checkfirst=True)
