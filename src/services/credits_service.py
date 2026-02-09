from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit import Credit
from src.models.payment import Payment
from src.schemas.responses import CreditClosedInfo, CreditOpenInfo, UserCreditsResponse


class CreditsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_credits(self, user_id: int) -> UserCreditsResponse:
        result = await self.session.execute(
            select(
                Credit,
                func.coalesce(func.sum(case((Payment.type_id == 1, Payment.sum), else_=0)), 0).label("body_paid"),
                func.coalesce(func.sum(case((Payment.type_id == 2, Payment.sum), else_=0)), 0).label("percent_paid"),
            )
            .outerjoin(Payment, Payment.credit_id == Credit.id)
            .where(Credit.user_id == user_id)
            .group_by(Credit.id)
        )

        items: list[CreditClosedInfo | CreditOpenInfo] = []

        for credit, body_paid, percent_paid in result.all():
            body_paid = Decimal(body_paid or 0)
            percent_paid = Decimal(percent_paid or 0)

            if credit.actual_return_date:
                total_paid = body_paid + percent_paid
                items.append(
                    CreditClosedInfo(
                        issuance_date=credit.issuance_date,
                        is_closed=True,
                        actual_return_date=credit.actual_return_date,
                        body=credit.body,
                        percent=credit.percent,
                        total_payments=total_paid,
                    )
                )
            else:
                today = date.today()
                overdue = max((today - credit.return_date).days, 0)
                items.append(
                    CreditOpenInfo(
                        issuance_date=credit.issuance_date,
                        is_closed=False,
                        return_date=credit.return_date,
                        overdue_days=overdue,
                        body=credit.body,
                        percent=credit.percent,
                        body_payments=body_paid,
                        percent_payments=percent_paid,
                    )
                )

        return UserCreditsResponse(credits=items)
