from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_job import AIJob
from app.schemas.workflow import AIJobStatusResponse

router = APIRouter(prefix="/api/ai-jobs", tags=["ai-jobs"])


@router.get("", response_model=list[AIJobStatusResponse])
async def list_ai_jobs(
    project_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AIJob)
    if project_id:
        query = query.filter(AIJob.project_id == project_id)
    query = query.order_by(AIJob.created_at.desc()).offset(offset).limit(limit)
    jobs = query.all()
    return [
        AIJobStatusResponse(
            job_id=j.id,
            project_id=j.project_id,
            workflow_execution_id=j.workflow_execution_id,
            status=j.status,
            progress=j.progress,
            model=j.model,
            output_url=f"/api/ai-jobs/{j.id}/download" if j.status == "completed" else None,
            error=j.error,
            created_at=j.created_at,
            started_at=j.started_at,
            completed_at=j.completed_at,
        )
        for j in jobs
    ]


@router.get("/{job_id}", response_model=AIJobStatusResponse)
async def get_ai_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AIJob).filter(AIJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    output_url = f"/api/ai-jobs/{job.id}/download" if job.status == "completed" else None

    return AIJobStatusResponse(
        job_id=job.id,
        project_id=job.project_id,
        workflow_execution_id=job.workflow_execution_id,
        status=job.status,
        progress=job.progress,
        model=job.model,
        output_url=output_url,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )


@router.get("/{job_id}/download")
async def download_ai_job_output(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AIJob).filter(AIJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    if not job.output_path or not Path(job.output_path).exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(job.output_path, media_type="video/mp4", filename=f"{job_id}.mp4")
