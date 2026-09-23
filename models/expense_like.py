from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ExpenseLike(Base):
    __tablename__ = "expense_likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "expense_id",
            name="uq_expense_likes_user_expense",
        ),
    )

    expense_like_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    expense_id: Mapped[int] = mapped_column(
        ForeignKey("expense_items.expense_id", ondelete="RESTRICT"),
        nullable=False,
    )
