from __future__ import annotations

from datetime import date

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.responses import (
    PlanInsertResponse,
    PlansPerformanceResponse,
    YearPerformanceResponse,
)
from src.services.plans_import_service import PlansImportService
from src.services.plans_monthly_service import PlansMonthlyService
from src.services.plans_year_service import PlansYearService


class PlansService:
    """
    Lightweight facade for compatibility with existing imports.
    File decomposition:
    - PlansImportService: insert_plans
    - PlansMonthlyService: plans_performance
    - PlansYearService: year_performance
    """

    def __init__(self, session: AsyncSession):
        self._import = PlansImportService(session)
        self._monthly = PlansMonthlyService(session)
        self._year = PlansYearService(session)

    async def insert_plans(self, file: UploadFile) -> PlanInsertResponse:
        return await self._import.insert_plans(file)

    async def plans_performance(self, as_of: date) -> PlansPerformanceResponse:
        return await self._monthly.plans_performance(as_of)

    async def year_performance(self, year: int) -> YearPerformanceResponse:
        return await self._year.year_performance(year)
