from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_jobs, assets, generate, health, projects, workflows
from app.config import settings
from app.database import SessionLocal, init_db
from app.models.project import Project

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(projects.router)
app.include_router(workflows.router)
app.include_router(ai_jobs.router)
app.include_router(assets.router)


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
