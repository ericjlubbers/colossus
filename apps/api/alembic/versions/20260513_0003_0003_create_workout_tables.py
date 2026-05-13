"""Create completed workout tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. completed_workouts
    op.create_table(
        "completed_workouts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["workout_templates.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_completed_workouts_user_id",
        "completed_workouts",
        ["user_id"],
    )
    op.create_index(
        "ix_completed_workouts_started_at",
        "completed_workouts",
        ["started_at"],
    )

    # 2. completed_sets
    op.create_table(
        "completed_sets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "workout_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "exercise_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("reps_completed", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Numeric(precision=7, scale=2), nullable=True),
        sa.Column(
            "is_warmup",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "is_failure",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("rpe", sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["workout_id"],
            ["completed_workouts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["block_id"],
            ["template_blocks.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_completed_sets_workout_id",
        "completed_sets",
        ["workout_id"],
    )
    op.create_index(
        "ix_completed_sets_exercise_id",
        "completed_sets",
        ["exercise_id"],
    )


def downgrade() -> None:
    op.drop_table("completed_sets")
    op.drop_table("completed_workouts")
