"""Add the places table.

Revision ID: b8f6a9592637
Revises: 0001_users_baseline
Create Date: 2026-10-11 19:11:55.324904
"""

from alembic import op
import sqlalchemy as sa


revision: str = "b8f6a9592637"
down_revision: str | None = "0001_users_baseline"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "places",
        sa.Column(
            "id",
            sa.Uuid(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("apple_place_id", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("apple_place_id", name="places_apple_place_id_key"),
    )


def downgrade() -> None:
    op.drop_table("places")
