"""add compliance review state

Revision ID: 20260923_0014
Revises: 20260923_0013
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260923_0014"
down_revision: str | None = "20260923_0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "compliance_mappings",
        sa.Column(
            "gap_status",
            sa.String(length=32),
            nullable=False,
            server_default="review_required",
        ),
    )
    op.add_column(
        "compliance_mappings",
        sa.Column("human_review_required", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("compliance_mappings", "human_review_required")
    op.drop_column("compliance_mappings", "gap_status")
