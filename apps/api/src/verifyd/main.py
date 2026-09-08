from contextlib import asynccontextmanager
import time
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from verifyd.config import get_settings
from verifyd.core.errors import (
    ConflictError,
    DomainStateError,
    NotFoundError,
    PermissionDeniedError,
    ProviderError,
    TransientAIError,
    ValidationError,
    VerifydError,
)
from verifyd.core.logging import generate_request_id, get_logger, request_id_ctx, setup_logging
from verifyd.db.session import async_engine, get_async_db
from verifyd.api.v1.auth import router as auth_router
from verifyd.api.v1.campaigns import router as campaigns_router
from verifyd.api.v1.contracts import router as contracts_router
from verifyd.api.v1.submissions import router as submissions_router
from verifyd.api.v1.reviews import router as reviews_router
from verifyd.api.v1.creators import router as creators_router
from verifyd.api.v1.admin import router as admin_router
from verifyd.api.v1.uploads import router as uploads_router

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Verifyd API", env=settings.ENVIRONMENT)
    yield
    logger.info("Shutting down Verifyd API")


app = FastAPI(
    title="Verifyd API",
    description="AI Compliance verification platform for influencer contracts against delivered videos.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or generate_request_id()
    token = request_id_ctx.set(req_id)
    start_time = time.time()

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "HTTP Request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
    finally:
        request_id_ctx.reset(token)


@app.exception_handler(VerifydError)
async def verifyd_error_handler(request: Request, exc: VerifydError):
    req_id = request_id_ctx.get()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "request_id": req_id,
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    req_id = request_id_ctx.get()
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "PERMISSION_DENIED",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_SERVER_ERROR",
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code_map.get(exc.status_code, "HTTP_ERROR"),
                "message": str(exc.detail),
                "details": {},
                "request_id": req_id,
            }
        },
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/ready")
async def ready(db: AsyncSession = Depends(get_async_db)):
    # Database check
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = False
        logger.warning("Readiness DB check failed", error=str(e))

    if not db_ok:
        return JSONResponse(status_code=503, content={"status": "not_ready", "database": "unavailable"})

    return {"status": "ready", "database": "connected", "redis": "connected"}


# Include Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(contracts_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
app.include_router(creators_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
