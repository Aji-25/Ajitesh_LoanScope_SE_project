"""extend approvals for durable human decisions

Revision ID: 20260923_0009
Revises: 20260923_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260923_0009"
down_revision: str | None = "20260923_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("approvals", sa.Column("workflow_thread_id", sa.String(120)))
    op.add_column(
        "approvals",
        sa.Column("request_payload", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.add_column(
        "approvals",
        sa.Column("decision_payload", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_approvals_workflow_thread_id", "approvals", ["workflow_thread_id"])


def downgrade() -> None:
    op.drop_index("ix_approvals_workflow_thread_id", table_name="approvals")
    op.drop_column("approvals", "decision_payload")
    op.drop_column("approvals", "request_payload")
    op.drop_column("approvals", "workflow_thread_id")
