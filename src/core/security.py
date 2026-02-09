from fastapi import Depends, Header, HTTPException, status

from src.core.config import get_settings


async def api_key_auth(x_api_key: str | None = Header(default=None, alias="X-API-Key"), settings=Depends(get_settings)) -> None:
    if x_api_key is None or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
