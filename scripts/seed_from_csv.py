import asyncio
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base, SessionLocal, engine
from src.models import Credit, Dictionary, Payment, Plan, User

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename: str):
    """Load tab-delimited CSV with dot-separated dates (dd.mm.yyyy)."""
    path = DATA_DIR / filename
    with path.open() as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    users_data = load_csv("users.csv")
    credits_data = load_csv("credits.csv")
    payments_data = load_csv("payments.csv")
    plans_data = load_csv("plans.csv")
    dictionary_data = load_csv("dictionary.csv")

    async with SessionLocal() as session:
        await seed_dictionary(session, dictionary_data)
        await seed_users(session, users_data)
        await seed_credits(session, credits_data)
        await seed_payments(session, payments_data)
        await seed_plans(session, plans_data)
        await session.commit()


async def seed_dictionary(session: AsyncSession, rows):
    for row in rows:
        session.add(Dictionary(id=int(row["id"]), name=row["name"]))


async def seed_users(session: AsyncSession, rows):
    for row in rows:
        session.add(
            User(
                id=int(row["id"]),
                login=row["login"],
                registration_date=datetime.strptime(row["registration_date"], "%d.%m.%Y").date(),
            )
        )


async def seed_credits(session: AsyncSession, rows):
    for row in rows:
        session.add(
            Credit(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                issuance_date=datetime.strptime(row["issuance_date"], "%d.%m.%Y").date(),
                return_date=datetime.strptime(row["return_date"], "%d.%m.%Y").date(),
                actual_return_date=datetime.strptime(row["actual_return_date"], "%d.%m.%Y").date()
                if row["actual_return_date"]
                else None,
                body=Decimal(row["body"]),
                percent=Decimal(row["percent"]),
            )
        )


async def seed_payments(session: AsyncSession, rows):
    for row in rows:
        session.add(
            Payment(
                id=int(row["id"]),
                sum=Decimal(row["sum"]),
                payment_date=datetime.strptime(row["payment_date"], "%d.%m.%Y").date(),
                credit_id=int(row["credit_id"]),
                type_id=int(row["type_id"]),
            )
        )


async def seed_plans(session: AsyncSession, rows):
    for row in rows:
        session.add(
            Plan(
                id=int(row["id"]),
                period=datetime.strptime(row["period"], "%d.%m.%Y").date(),
                sum=Decimal(row["sum"]),
                category_id=int(row["category_id"]),
            )
        )


if __name__ == "__main__":
    asyncio.run(seed())
