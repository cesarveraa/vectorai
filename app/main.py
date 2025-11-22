
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from .core.config import settings
from .core.ratelimit import rate_limit_middleware
from .routers import clients, detect_vector, detect_image
from .routers import reports




app = FastAPI(title="Face API", version="1.0.0", openapi_url=f"{settings.API_PREFIX}/openapi.json")


# Rate limit
app.middleware("http")(rate_limit_middleware)


# CORS
app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"ok": True}


# Mount routers
app.include_router(clients.router, prefix=settings.API_PREFIX)
app.include_router(detect_vector.router, prefix=settings.API_PREFIX)
app.include_router(detect_image.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)


# Global exception handler example
@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal error", "hint": str(exc) if settings.ENV != "prod" else None})