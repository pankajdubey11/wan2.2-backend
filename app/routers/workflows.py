from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workflow import GenerateWorkflowRequest, GenerateWorkflowResponse
from app.services.ai_gateway_service import create_generation_workflow, start_generation_job

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/generate", response_model=GenerateWorkflowResponse)
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
