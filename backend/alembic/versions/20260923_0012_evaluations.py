"""add project evaluation snapshots

Revision ID: 20260923_0012
Revises: 20260923_0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0012"
down_revision: str | None = "20260923_0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_evaluation_runs_project_id", "evaluation_runs", ["project_id"])


def downgrade() -> None:
    op.drop_table("evaluation_runs")
