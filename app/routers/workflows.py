from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.workflow_execution import WorkflowExecution
from app.schemas.workflow import (
    GenerateWorkflowRequest,
    GenerateWorkflowResponse,
    WorkflowExecutionResponse,
)
from app.services.ai_gateway_service import create_generation_workflow, start_generation_job

router = APIRouter(prefix="/api/workflows", tags=["workflows"])

GENERATE_EXAMPLES = {
    "text-to-video": {
        "summary": "Text-to-video generation",
        "value": {
            "project_id": "550e8400-e29b-41d4-a716-446655440000",
            "model": "ti2v-5b",
            "prompt": "A cinematic shot of a mountain landscape at sunset",
            "steps": 30,
            "guidance_scale": 6.0,
            "size": "704*1280",
        },
    },
    "image-to-video": {
        "summary": "Image-to-video generation",
        "value": {
            "project_id": "550e8400-e29b-41d4-a716-446655440000",
            "model": "i2v-14b",
            "prompt": "Make the waves move gently",
            "image": "<base64 encoded image>",
            "steps": 40,
            "guidance_scale": 7.0,
        },
    },
}


@router.get("", response_model=list[WorkflowExecutionResponse])
async def list_workflows(
    project_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(WorkflowExecution)
    if project_id:
        query = query.filter(WorkflowExecution.project_id == project_id)
    query = query.order_by(WorkflowExecution.created_at.desc()).offset(offset).limit(limit)
    workflows = query.all()
    return [
        WorkflowExecutionResponse(
            id=w.id,
            project_id=w.project_id,
            workflow_type=w.workflow_type,
            status=w.status,
            progress=w.progress,
            error=w.error,
            created_at=w.created_at,
            started_at=w.started_at,
            completed_at=w.completed_at,
        )
        for w in workflows
    ]


@router.post(
    "/generate",
    response_model=GenerateWorkflowResponse,
    openapi_extra={"examples": GENERATE_EXAMPLES},
)
async def generate_workflow(req: GenerateWorkflowRequest, db: Session = Depends(get_db)):
    try:
        workflow, job = create_generation_workflow(db, req)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    start_generation_job(job.id)

    return GenerateWorkflowResponse(
        workflow_execution_id=workflow.id,
        job_id=job.id,
        status=job.status,
        estimated_seconds=540,
    )
