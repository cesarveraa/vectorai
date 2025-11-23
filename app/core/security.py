from fastapi import Header, HTTPException, status
from .config import settings
from typing import Optional

async def api_key_guard(x_api_key: Optional[str] = Header(default=None)):
    
    return True