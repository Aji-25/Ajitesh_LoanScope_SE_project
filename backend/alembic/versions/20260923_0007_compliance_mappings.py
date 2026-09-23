"""add evidence grounded compliance mappings

Revision ID: 20260923_0007
Revises: 20260923_0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0007"
down_revision: str | None = "20260923_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "compliance_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requirement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("obligation", sa.Text(), nullable=False),
        sa.Column("applicability", sa.String(length=32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("evidence_chunk_ids", postgresql.JSONB(), nullable=False),
        sa.Column("citations", postgresql.JSONB(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_mappings_project_id", "compliance_mappings", ["project_id"])
    op.create_index(
        "ix_compliance_mappings_requirement_id", "compliance_mappings", ["requirement_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_compliance_mappings_requirement_id", table_name="compliance_mappings")
    op.drop_index("ix_compliance_mappings_project_id", table_name="compliance_mappings")
    op.drop_table("compliance_mappings")
