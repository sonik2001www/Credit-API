from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Credit(Base):
    __tablename__ = "credits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    issuance_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    body: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    percent: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    user: Mapped["User"] = relationship(back_populates="credits")
    payments: Mapped[list["Payment"]] = relationship(back_populates="credit", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - for debug only
        return f"Credit(id={self.id}, user_id={self.user_id})"
