from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import api_key_auth
from src.core.database import get_session
from src.schemas.responses import UserCreditsResponse
from src.services.credits import CreditsService

router = APIRouter(prefix="/user_credits", tags=["credits"], dependencies=[Depends(api_key_auth)])


@router.get("/{user_id}", response_model=UserCreditsResponse)
async def user_credits(user_id: int, session: AsyncSession = Depends(get_session)) -> UserCreditsResponse:
    service = CreditsService(session)
    return await service.get_user_credits(user_id)
