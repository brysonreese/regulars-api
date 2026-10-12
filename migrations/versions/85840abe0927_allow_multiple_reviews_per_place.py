"""Allow multiple reviews by one user for one place.

Revision ID: 85840abe0927
Revises: fd4c90a2c6cc
Create Date: 2026-10-11 19:55:11.537582
"""

from alembic import op
import sqlalchemy as sa


revision: str = "85840abe0927"
down_revision: str | None = "fd4c90a2c6cc"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.drop_constraint("reviews_user_place_key", "reviews", type_="unique")
    op.create_index("ix_reviews_user_id", "reviews", ["user_id"])


def downgrade() -> None:
    duplicate = op.get_bind().execute(
        sa.text(
            "SELECT 1 FROM reviews "
            "GROUP BY user_id, place_id HAVING count(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            "Cannot restore one-review-per-place constraint while duplicate reviews exist"
        )

    op.drop_index("ix_reviews_user_id", table_name="reviews")
    op.create_unique_constraint(
        "reviews_user_place_key", "reviews", ["user_id", "place_id"]
    )
