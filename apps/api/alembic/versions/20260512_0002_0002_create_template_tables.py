"""Create workout template tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# ── Enum definitions ──────────────────────────────────────────────────────────

blocktype_enum = postgresql.ENUM(
    "set",
    "superset",
    name="blocktype",
    create_type=False,
)


def upgrade() -> None:
    # 1. Create enum type
    blocktype_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create workout_templates table
    op.create_table(
        "workout_templates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            server_default=sa.text("'{}'"),
            nullable=False,
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
    op.create_index("ix_workout_templates_user_id", "workout_templates", ["user_id"])
    op.create_index("ix_workout_templates_name", "workout_templates", ["name"])

    # 3. Create template_blocks table
    op.create_table(
        "template_blocks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("block_type", blocktype_enum, nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("rest_after_seconds", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["workout_templates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_template_blocks_template_id", "template_blocks", ["template_id"]
    )

    # 4. Create template_block_exercises table
    op.create_table(
        "template_block_exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("block_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "order_in_block",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "sets",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("progression_override", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(
            ["block_id"],
            ["template_blocks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tbe_block_id", "template_block_exercises", ["block_id"])
    op.create_index("ix_tbe_exercise_id", "template_block_exercises", ["exercise_id"])


def downgrade() -> None:
    op.drop_table("template_block_exercises")
    op.drop_table("template_blocks")
    op.drop_table("workout_templates")
    blocktype_enum.drop(op.get_bind(), checkfirst=True)
