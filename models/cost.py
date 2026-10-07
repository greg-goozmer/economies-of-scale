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


class Cost(Base):
    __tablename__ = "costs"
    __table_args__ = (
        CheckConstraint(
            "cost_status IN ('draft', 'published', 'deleted')",
            name="ck_costs_status",
        ),
        CheckConstraint(
            "cost_behavior IS NULL "
            "OR cost_behavior IN ('fixed', 'variable')",
            name="ck_costs_behavior",
        ),
        CheckConstraint(
            "cost_code IS NULL OR cost_code >= 0",
            name="ck_costs_code_nonnegative",
        ),
        Index("ix_costs_status", "cost_status"),
        Index("ix_costs_code", "cost_code"),
        Index(
            "uq_costs_one_draft_per_creator",
            "cost_creator_id",
            unique=True,
            postgresql_where=text("cost_status = 'draft'"),
        ),
    )

    cost_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_name: Mapped[str] = mapped_column(String(100), nullable=False)
    cost_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    cost_status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="draft",
        server_default="draft",
    )
    cost_image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    cost_video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    cost_behavior: Mapped[str | None] = mapped_column(String(16), nullable=True)
    cost_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    cost_creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    cost_formed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
