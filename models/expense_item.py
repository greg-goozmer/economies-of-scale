from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.base import Base


class ExpenseItem(Base):
    __tablename__ = "expense_items"
    __table_args__ = (
        CheckConstraint(
            "expense_status IN ('draft', 'published', 'deleted')",
            name="ck_expense_items_status",
        ),
        CheckConstraint(
            "expense_behavior IS NULL "
            "OR expense_behavior IN ('fixed', 'variable')",
            name="ck_expense_items_behavior",
        ),
        CheckConstraint(
            "expense_code IS NULL OR expense_code >= 0",
            name="ck_expense_items_code_nonnegative",
        ),
        Index("ix_expense_items_status", "expense_status"),
        Index("ix_expense_items_code", "expense_code"),
        Index(
            "uq_expense_items_one_draft_per_creator",
            "expense_creator_id",
            unique=True,
            postgresql_where=text("expense_status = 'draft'"),
        ),
    )

    expense_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    expense_name: Mapped[str] = mapped_column(String(100), nullable=False)
    expense_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    expense_status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    expense_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expense_video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    expense_behavior: Mapped[str | None] = mapped_column(String(16), nullable=True)
    expense_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expense_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expense_creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    expense_formed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
