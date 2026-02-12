from datetime import date

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import api_key_auth
from src.core.database import get_session
from src.schemas.responses import PlanInsertResponse, PlansPerformanceResponse, YearPerformanceResponse
from src.services.plans_service import PlansService

router = APIRouter(prefix="/plans", tags=["plans"], dependencies=[Depends(api_key_auth)])


@router.post("/insert", response_model=PlanInsertResponse)
async def plans_insert(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> PlanInsertResponse:
    service = PlansService(session)
    return await service.insert_plans(file)


@router.get("/performance", response_model=PlansPerformanceResponse)
async def plans_performance(
    report_date: date = Query(..., description="Date for performance calculation"),
    session: AsyncSession = Depends(get_session),
) -> PlansPerformanceResponse:
    service = PlansService(session)
    return await service.plans_performance(report_date)


@router.get("/year_performance", response_model=YearPerformanceResponse)
async def year_performance(
    year: int = Query(..., ge=1900, le=2100),
    session: AsyncSession = Depends(get_session),
) -> YearPerformanceResponse:
    service = PlansService(session)
    return await service.year_performance(year)
