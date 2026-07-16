import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import SessionLocal, init_db
from app.models.project import Project
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_jobs, analytics, assets, generate, health, notifications, projects, workflows

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details=None,
):
    request_id = getattr(request.state, "request_id", None)
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request_id": request_id,
    }
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
    code = f"HTTP_{exc.status_code}"
    return _error_response(
        request=request,
        status_code=exc.status_code,
        code=code,
        message=detail,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(
        request=request,
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=exc.errors(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception request_id=%s", getattr(request.state, "request_id", None))
    return _error_response(
        request=request,
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Unexpected server error",
    )

app.include_router(health.router, tags=["health"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(projects.router)
app.include_router(workflows.router)
app.include_router(ai_jobs.router)
app.include_router(assets.router)
app.include_router(notifications.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    # Initialize database tables
    init_db()

    # Seed a default project for local development.
    db = SessionLocal()
    try:
        existing = db.query(Project).first()
        if not existing:
            default_project = Project(name="Default Project", description="Auto-created for local development")
            db.add(default_project)
            db.commit()
            db.refresh(default_project)
            print(f"  Seeded default project: {default_project.id}")
    finally:
        db.close()

    print(f"  Mode: {'MOCK' if settings.is_mock else 'LIVE'}")
    print(f"  DB: {settings.DATABASE_URL}")
    print(f"  Worker: {'MockWorker' if settings.is_mock else 'Wan2_2Worker'}")
    print(f"  Output: {settings.OUTPUT_DIR}")
    print(f"  API: http://localhost:{settings.PORT}")
