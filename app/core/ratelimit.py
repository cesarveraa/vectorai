import time
from fastapi import Request, HTTPException, status
from typing import Dict, Tuple


_BUCKETS: Dict[str, Tuple[float, int]] = {}
RATE = 60 # tokens per minute
WINDOW = 60.0


async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host if request.client else "anon"
    now = time.monotonic()
    refill_time, tokens = _BUCKETS.get(ip, (now, RATE))
    delta = max(0.0, now - refill_time)
    tokens = min(RATE, tokens + int(delta * (RATE / WINDOW)))
    if tokens <= 0:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    _BUCKETS[ip] = (now, tokens - 1)
    response = await call_next(request)
    return response