from __future__ import annotations

from decimal import Decimal
from io import BytesIO

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.dictionary import Dictionary
from src.models.plan import Plan
from src.schemas.responses import PlanInsertResponse


class PlansImportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_plans(self, file: UploadFile) -> PlanInsertResponse:
        content = await file.read()

        df = pd.read_excel(BytesIO(content))
        required_columns = {"period", "category", "sum"}

        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid columns in file")

        df["period"] = pd.to_datetime(df["period"], errors="coerce")
        if df["period"].isna().any():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid period values")

        if not all(dt.day == 1 for dt in df["period"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Period must be first day of month")

        if df["sum"].isna().any():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sum must not be empty")

        inserted = 0

        for _, row in df.iterrows():
            period = row["period"].date()
            category_name = str(row["category"]).strip()
            amount = Decimal(str(row["sum"]))

            category = await self.session.scalar(select(Dictionary).where(Dictionary.name == category_name))

            if not category:
                category = Dictionary(name=category_name)
                self.session.add(category)
                await self.session.flush()

            exists = await self.session.scalar(
                select(func.count()).where(and_(Plan.period == period, Plan.category_id == category.id))
            )

            if exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plan for {period} and {category_name} already exists",
                )

            plan = Plan(period=period, sum=amount, category_id=category.id)
            self.session.add(plan)
            inserted += 1

        await self.session.commit()
        return PlanInsertResponse(inserted=inserted, message="Plans inserted")
