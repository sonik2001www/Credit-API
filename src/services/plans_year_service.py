from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit import Credit
from src.models.dictionary import Dictionary
from src.models.payment import Payment
from src.models.plan import Plan
from src.schemas.responses import YearPerformanceItem, YearPerformanceResponse


class PlansYearService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def year_performance(self, year: int) -> YearPerformanceResponse:
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)

        issuance_labels = {"видача"}

        issuance_total = Decimal(
            await self.session.scalar(
                select(func.coalesce(func.sum(Credit.body), 0)).where(Credit.issuance_date.between(year_start, year_end))
            )
        )
        payment_total = Decimal(
            await self.session.scalar(
                select(func.coalesce(func.sum(Payment.sum), 0)).where(Payment.payment_date.between(year_start, year_end))
            )
        )

        issuance_rows = await self.session.execute(
            select(
                func.year(Credit.issuance_date).label("y"),
                func.month(Credit.issuance_date).label("m"),
                func.coalesce(func.sum(Credit.body), 0).label("sum_body"),
                func.count().label("cnt"),
            )
            .where(Credit.issuance_date.between(year_start, year_end))
            .group_by("y", "m")
        )
        issuance_by_month = {(int(r.y), int(r.m)): (Decimal(r.sum_body), int(r.cnt)) for r in issuance_rows}

        payment_rows = await self.session.execute(
            select(
                func.year(Payment.payment_date).label("y"),
                func.month(Payment.payment_date).label("m"),
                func.coalesce(func.sum(Payment.sum), 0).label("sum_pay"),
                func.count().label("cnt"),
            )
            .where(Payment.payment_date.between(year_start, year_end))
            .group_by("y", "m")
        )
        payment_by_month = {(int(r.y), int(r.m)): (Decimal(r.sum_pay), int(r.cnt)) for r in payment_rows}

        issuance_plan_rows = await self.session.execute(
            select(
                func.year(Plan.period).label("y"),
                func.month(Plan.period).label("m"),
                func.coalesce(func.sum(Plan.sum), 0).label("sum_plan"),
            )
            .join(Dictionary, Plan.category_id == Dictionary.id)
            .where(func.lower(Dictionary.name).in_(issuance_labels), Plan.period.between(year_start, year_end))
            .group_by("y", "m")
        )
        issuance_plan_by_month = {(int(r.y), int(r.m)): Decimal(r.sum_plan) for r in issuance_plan_rows}

        payment_plan_rows = await self.session.execute(
            select(
                func.year(Plan.period).label("y"),
                func.month(Plan.period).label("m"),
                func.coalesce(func.sum(Plan.sum), 0).label("sum_plan"),
            )
            .join(Dictionary, Plan.category_id == Dictionary.id)
            .where(~func.lower(Dictionary.name).in_(issuance_labels), Plan.period.between(year_start, year_end))
            .group_by("y", "m")
        )
        payment_plan_by_month = {(int(r.y), int(r.m)): Decimal(r.sum_plan) for r in payment_plan_rows}

        items: list[YearPerformanceItem] = []
        for month in range(1, 13):
            key = (year, month)
            issuance_sum, issuance_count = issuance_by_month.get(key, (Decimal("0"), 0))
            payment_sum, payment_count = payment_by_month.get(key, (Decimal("0"), 0))
            issuance_plan_sum = issuance_plan_by_month.get(key, Decimal("0"))
            payment_plan_sum = payment_plan_by_month.get(key, Decimal("0"))

            issuance_completion = float(issuance_sum / issuance_plan_sum * 100) if issuance_plan_sum != 0 else 100.0
            payment_completion = float(payment_sum / payment_plan_sum * 100) if payment_plan_sum != 0 else 100.0

            issuance_share = float(issuance_sum / issuance_total * 100) if issuance_total != 0 else 0.0
            payment_share = float(payment_sum / payment_total * 100) if payment_total != 0 else 0.0

            items.append(
                YearPerformanceItem(
                    month=month,
                    year=year,
                    issuance_count=issuance_count,
                    issuance_plan_sum=issuance_plan_sum,
                    issuance_sum=issuance_sum,
                    issuance_completion=round(issuance_completion, 2),
                    payment_count=payment_count,
                    payment_plan_sum=payment_plan_sum,
                    payment_sum=payment_sum,
                    payment_completion=round(payment_completion, 2),
                    issuance_month_share=round(issuance_share, 2),
                    payment_month_share=round(payment_share, 2),
                )
            )

        return YearPerformanceResponse(items=items)
