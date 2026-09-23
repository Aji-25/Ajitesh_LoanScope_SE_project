"""add persistent requirement quality findings

Revision ID: 20260923_0005
Revises: 20260923_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0005"
down_revision: str | None = "20260923_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "requirements",
        sa.Column("quality_findings", postgresql.JSONB(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "requirements",
        sa.Column(
            "clarification_status",
            sa.String(length=32),
            nullable=False,
            server_default="not_required",
        ),
    )
    op.add_column(
        "requirements", sa.Column("version", sa.Integer(), nullable=False, server_default="1")
    )


def downgrade() -> None:
    op.drop_column("requirements", "version")
    op.drop_column("requirements", "clarification_status")
    op.drop_column("requirements", "quality_findings")
