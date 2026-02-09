from datetime import date
from decimal import Decimal
from typing import List, Union

from pydantic import BaseModel, ConfigDict


class CreditBase(BaseModel):
    issuance_date: date
    is_closed: bool

    model_config = ConfigDict(from_attributes=True)


class CreditClosedInfo(CreditBase):
    actual_return_date: date
    body: Decimal
    percent: Decimal
    total_payments: Decimal


class CreditOpenInfo(CreditBase):
    return_date: date
    overdue_days: int
    body: Decimal
    percent: Decimal
    body_payments: Decimal
    percent_payments: Decimal


class UserCreditsResponse(BaseModel):
    credits: List[Union[CreditClosedInfo, CreditOpenInfo]]

    model_config = ConfigDict(from_attributes=True)


class PlanInsertResponse(BaseModel):
    inserted: int
    message: str


class PlanPerformanceItem(BaseModel):
    period: date
    category: str
    plan_sum: Decimal
    fact_sum: Decimal
    completion: float


class PlansPerformanceResponse(BaseModel):
    items: List[PlanPerformanceItem]


class YearPerformanceItem(BaseModel):
    month: int
    year: int
    issuance_count: int
    issuance_plan_sum: Decimal
    issuance_sum: Decimal
    issuance_completion: float
    payment_count: int
    payment_plan_sum: Decimal
    payment_sum: Decimal
    payment_completion: float
    issuance_month_share: float
    payment_month_share: float


class YearPerformanceResponse(BaseModel):
    items: List[YearPerformanceItem]
