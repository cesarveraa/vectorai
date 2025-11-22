from fastapi import Header, HTTPException, status
from .config import settings
from typing import Optional

async def api_key_guard(x_api_key: Optional[str] = Header(default=None)):
    if not x_api_key or x_api_key != settings.INTERNAL_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True