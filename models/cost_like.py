from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class CostLike(Base):
    __tablename__ = "cost_likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "cost_id",
            name="uq_cost_likes_user_cost",
        ),
    )

    cost_like_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    cost_id: Mapped[int] = mapped_column(
        ForeignKey("costs.cost_id", ondelete="RESTRICT"),
        nullable=False,
    )
