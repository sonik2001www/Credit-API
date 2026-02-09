from fastapi import APIRouter

from src.api.v1.endpoints import credits, plans

router = APIRouter(prefix="/v1")

router.include_router(credits.router)
router.include_router(plans.router)
