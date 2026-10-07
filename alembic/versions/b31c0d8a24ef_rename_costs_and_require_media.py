"""Rename the subject tables and require credentials and media URLs.

Revision ID: b31c0d8a24ef
Revises: 2d11b8767f7a
"""

from alembic import op
import sqlalchemy as sa


revision = "b31c0d8a24ef"
down_revision = "2d11b8767f7a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("expense_items", "costs")
    op.rename_table("expense_likes", "cost_likes")

    for old, new in (
        ("expense_id", "cost_id"),
        ("expense_name", "cost_name"),
        ("expense_description", "cost_description"),
        ("expense_status", "cost_status"),
        ("expense_image_url", "cost_image_url"),
        ("expense_video_url", "cost_video_url"),
        ("expense_behavior", "cost_behavior"),
        ("expense_code", "cost_code"),
        ("expense_created_at", "cost_created_at"),
        ("expense_creator_id", "cost_creator_id"),
        ("expense_formed_at", "cost_formed_at"),
    ):
        op.alter_column("costs", old, new_column_name=new)

    op.alter_column("cost_likes", "expense_like_id", new_column_name="cost_like_id")
    op.alter_column("cost_likes", "expense_id", new_column_name="cost_id")

    op.execute("ALTER SEQUENCE expense_items_expense_id_seq RENAME TO costs_cost_id_seq")
    op.execute("ALTER SEQUENCE expense_likes_expense_like_id_seq RENAME TO cost_likes_cost_like_id_seq")
    for table, old, new in (
        ("costs", "expense_items_pkey", "costs_pkey"),
        ("costs", "ck_expense_items_status", "ck_costs_status"),
        ("costs", "ck_expense_items_behavior", "ck_costs_behavior"),
        ("costs", "ck_expense_items_code_nonnegative", "ck_costs_code_nonnegative"),
        ("costs", "expense_items_expense_creator_id_fkey", "costs_cost_creator_id_fkey"),
        ("cost_likes", "expense_likes_pkey", "cost_likes_pkey"),
        ("cost_likes", "expense_likes_user_id_fkey", "cost_likes_user_id_fkey"),
        ("cost_likes", "expense_likes_expense_id_fkey", "cost_likes_cost_id_fkey"),
        ("cost_likes", "uq_expense_likes_user_expense", "uq_cost_likes_user_cost"),
    ):
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new}")
    for old, new in (
        ("ix_expense_items_status", "ix_costs_status"),
        ("ix_expense_items_code", "ix_costs_code"),
        ("uq_expense_items_one_draft_per_creator", "uq_costs_one_draft_per_creator"),
    ):
        op.execute(f"ALTER INDEX {old} RENAME TO {new}")

    op.add_column("users", sa.Column("user_password_hash", sa.String(255), nullable=True))
    op.execute("UPDATE users SET user_password_hash = '!' WHERE user_password_hash IS NULL")
    op.alter_column("users", "user_password_hash", nullable=False)

    op.execute(
        "UPDATE costs SET cost_image_url = "
        "'http://localhost:9000/costs/missing-image.png' "
        "WHERE cost_image_url IS NULL OR cost_image_url = ''"
    )
    op.execute(
        "UPDATE costs SET cost_video_url = "
        "'http://localhost:9000/costs/missing-video.mp4' "
        "WHERE cost_video_url IS NULL OR cost_video_url = ''"
    )
    op.execute(
        "UPDATE costs SET cost_image_url = replace(cost_image_url, '/expense-items/', '/costs/'), "
        "cost_video_url = replace(cost_video_url, '/expense-items/', '/costs/')"
    )
    op.alter_column("costs", "cost_image_url", nullable=False)
    op.alter_column("costs", "cost_video_url", nullable=False)


def downgrade() -> None:
    op.alter_column("costs", "cost_image_url", nullable=True)
    op.alter_column("costs", "cost_video_url", nullable=True)
    op.execute(
        "UPDATE costs SET cost_image_url = replace(cost_image_url, '/costs/', '/expense-items/'), "
        "cost_video_url = replace(cost_video_url, '/costs/', '/expense-items/')"
    )
    op.drop_column("users", "user_password_hash")

    for old, new in (
        ("ix_costs_status", "ix_expense_items_status"),
        ("ix_costs_code", "ix_expense_items_code"),
        ("uq_costs_one_draft_per_creator", "uq_expense_items_one_draft_per_creator"),
    ):
        op.execute(f"ALTER INDEX {old} RENAME TO {new}")
    for table, old, new in (
        ("costs", "costs_pkey", "expense_items_pkey"),
        ("costs", "ck_costs_status", "ck_expense_items_status"),
        ("costs", "ck_costs_behavior", "ck_expense_items_behavior"),
        ("costs", "ck_costs_code_nonnegative", "ck_expense_items_code_nonnegative"),
        ("costs", "costs_cost_creator_id_fkey", "expense_items_expense_creator_id_fkey"),
        ("cost_likes", "cost_likes_pkey", "expense_likes_pkey"),
        ("cost_likes", "cost_likes_user_id_fkey", "expense_likes_user_id_fkey"),
        ("cost_likes", "cost_likes_cost_id_fkey", "expense_likes_expense_id_fkey"),
        ("cost_likes", "uq_cost_likes_user_cost", "uq_expense_likes_user_expense"),
    ):
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old} TO {new}")
    op.execute("ALTER SEQUENCE costs_cost_id_seq RENAME TO expense_items_expense_id_seq")
    op.execute("ALTER SEQUENCE cost_likes_cost_like_id_seq RENAME TO expense_likes_expense_like_id_seq")

    op.alter_column("cost_likes", "cost_like_id", new_column_name="expense_like_id")
    op.alter_column("cost_likes", "cost_id", new_column_name="expense_id")
    for old, new in (
        ("cost_id", "expense_id"),
        ("cost_name", "expense_name"),
        ("cost_description", "expense_description"),
        ("cost_status", "expense_status"),
        ("cost_image_url", "expense_image_url"),
        ("cost_video_url", "expense_video_url"),
        ("cost_behavior", "expense_behavior"),
        ("cost_code", "expense_code"),
        ("cost_created_at", "expense_created_at"),
        ("cost_creator_id", "expense_creator_id"),
        ("cost_formed_at", "expense_formed_at"),
    ):
        op.alter_column("costs", old, new_column_name=new)
    op.rename_table("cost_likes", "expense_likes")
    op.rename_table("costs", "expense_items")
