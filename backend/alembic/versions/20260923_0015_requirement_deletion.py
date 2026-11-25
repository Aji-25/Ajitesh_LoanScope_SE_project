"""Keep deleted requirements out of the active baseline.

Revision ID: 20260923_0015
Revises: 20260923_0014
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260923_0015"
down_revision: str | None = "20260923_0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("requirements", sa.Column("deleted_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("requirements", "deleted_at")
