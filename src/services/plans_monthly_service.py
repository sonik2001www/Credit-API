from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit import Credit
from src.models.dictionary import Dictionary
from src.models.payment import Payment
from src.models.plan import Plan
from src.schemas.responses import PlanPerformanceItem, PlansPerformanceResponse


class PlansMonthlyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def plans_performance(self, as_of: date) -> PlansPerformanceResponse:
        """
        Returns the execution of plans for a specific month (period = first day of month as_of).
        Avoids N+1: one query for plans + up to two aggregate queries for facts.
        """
        month_start = date(as_of.year, as_of.month, 1)

        plans_result = await self.session.execute(
            select(Plan, Dictionary.name)
            .join(Dictionary, Plan.category_id == Dictionary.id)
            .where(Plan.period == month_start)
        )
        plans = plans_result.all()

        if not plans:
            return PlansPerformanceResponse(items=[])

        issuance_periods = {
            plan.period for plan, name in plans if name.lower().startswith("видача") or "issu" in name.lower()
        }
        payment_periods = {
            plan.period for plan, name in plans if not (name.lower().startswith("видача") or "issu" in name.lower())
        }

        issuance_sums: dict[date, Decimal] = {}
        if issuance_periods:
            issuance_rows = await self.session.execute(
                select(
                    Plan.period,
                    func.coalesce(func.sum(Credit.body), 0).label("sum_body"),
                )
                .join(Dictionary, Plan.category_id == Dictionary.id)
                .join(Credit, Credit.issuance_date.between(Plan.period, as_of))
                .where(or_(Dictionary.name.ilike("видача%"), Dictionary.name.ilike("%issu%")))
                .where(Plan.period.in_(issuance_periods))
                .group_by(Plan.period)
            )
            issuance_sums = {row.period: Decimal(row.sum_body) for row in issuance_rows}

        payment_sums: dict[date, Decimal] = {}
        if payment_periods:
            payment_rows = await self.session.execute(
                select(
                    Plan.period,
                    func.coalesce(func.sum(Payment.sum), 0).label("sum_pay"),
                )
                .join(Dictionary, Plan.category_id == Dictionary.id)
                .join(Payment, Payment.payment_date.between(Plan.period, as_of))
                .where(~or_(Dictionary.name.ilike("видача%"), Dictionary.name.ilike("%issu%")))
                .where(Plan.period.in_(payment_periods))
                .group_by(Plan.period)
            )
            payment_sums = {row.period: Decimal(row.sum_pay) for row in payment_rows}

        items: list[PlanPerformanceItem] = []
        for plan, category_name in plans:
            if category_name.lower().startswith("видача") or "issu" in category_name.lower():
                fact_sum = issuance_sums.get(plan.period, Decimal("0"))
            else:
                fact_sum = payment_sums.get(plan.period, Decimal("0"))

            completion = float(fact_sum / plan.sum * 100) if plan.sum != 0 else 100.0
            items.append(
                PlanPerformanceItem(
                    period=plan.period,
                    category=category_name,
                    plan_sum=plan.sum,
                    fact_sum=fact_sum,
                    completion=round(completion, 2),
                )
            )

        return PlansPerformanceResponse(items=items)
