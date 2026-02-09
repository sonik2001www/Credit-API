from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sum: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    credit_id: Mapped[int] = mapped_column(ForeignKey("credits.id", ondelete="CASCADE"), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"), nullable=False)

    credit: Mapped["Credit"] = relationship(back_populates="payments")

    def __repr__(self) -> str:  # pragma: no cover - for debug only
        return f"Payment(id={self.id}, credit_id={self.credit_id}, sum={self.sum})"
