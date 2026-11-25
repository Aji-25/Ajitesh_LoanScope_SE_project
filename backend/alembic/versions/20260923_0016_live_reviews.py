"""Store model-backed review details.

Revision ID: 20260923_0016
Revises: 20260923_0015
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "20260923_0016"
down_revision: str | None = "20260923_0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("risks", sa.Column("existing_control", sa.Text()))
    op.add_column("risks", sa.Column("rating_reason", sa.Text()))
    op.add_column("evaluation_runs", sa.Column("review_actions", JSONB()))
    op.add_column("compliance_mappings", sa.Column("ai_reviewed", sa.Boolean()))


def downgrade() -> None:
    op.drop_column("compliance_mappings", "ai_reviewed")
    op.drop_column("evaluation_runs", "review_actions")
    op.drop_column("risks", "rating_reason")
    op.drop_column("risks", "existing_control")
