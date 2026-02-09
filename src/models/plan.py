from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Plan(Base):
    __tablename__ = "plans"
    __table_args__ = (UniqueConstraint("period", "category_id", name="uq_plan_period_category"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    period: Mapped[date] = mapped_column(Date, nullable=False)
    sum: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("dictionary.id"), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - for debug only
        return f"Plan(id={self.id}, period={self.period}, category_id={self.category_id})"
