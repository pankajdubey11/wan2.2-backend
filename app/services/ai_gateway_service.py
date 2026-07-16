import base64
import datetime
import threading
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.ai_job import AIJob
from app.models.project import Project
from app.models.workflow_execution import WorkflowExecution
from app.schemas.workflow import GenerateWorkflowRequest
from app.services.event_service import emit_event
from app.services.mock_worker import MockWorker
from app.services.wan_worker import Wan2_2Worker

JOB_STATUS_QUEUED = "queued"
JOB_STATUS_PROCESSING = "processing"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"

WORKFLOW_STATUS_QUEUED = "queued"
WORKFLOW_STATUS_PROCESSING = "processing"
WORKFLOW_STATUS_COMPLETED = "completed"
WORKFLOW_STATUS_FAILED = "failed"

_ALLOWED_TRANSITIONS = {
    JOB_STATUS_QUEUED: {JOB_STATUS_PROCESSING, JOB_STATUS_FAILED},
    JOB_STATUS_PROCESSING: {JOB_STATUS_COMPLETED, JOB_STATUS_FAILED},
    JOB_STATUS_COMPLETED: set(),
    JOB_STATUS_FAILED: set(),
}


def _get_worker():
    if settings.is_mock or not Path(settings.WAN2_2_PATH).exists():
        return MockWorker()
    return Wan2_2Worker(
        wan_path=settings.WAN2_2_PATH,
        ckpt_dir=settings.WAN2_2_CKPT_DIR,
    )


def _transition_ai_job(
    db: Session,
    job: AIJob,
    new_status: str,
    *,
    progress: float | None = None,
    error: str | None = None,
) -> None:
    if new_status not in _ALLOWED_TRANSITIONS.get(job.status, set()):
        raise ValueError(f"Invalid transition: {job.status} -> {new_status}")

    job.status = new_status
    if progress is not None:
        job.progress = progress
    if error is not None:
        job.error = error
    if new_status == JOB_STATUS_PROCESSING:
        job.started_at = datetime.datetime.utcnow()
    if new_status in {JOB_STATUS_COMPLETED, JOB_STATUS_FAILED}:
        job.completed_at = datetime.datetime.utcnow()
    db.commit()


def _transition_workflow(
    db: Session,
    workflow: WorkflowExecution,
    status: str,
    *,
    progress: float | None = None,
    error: str | None = None,
) -> None:
    workflow.status = status
    if progress is not None:
        workflow.progress = progress
    if error is not None:
        workflow.error = error
    if status == WORKFLOW_STATUS_PROCESSING:
        workflow.started_at = datetime.datetime.utcnow()
    if status in {WORKFLOW_STATUS_COMPLETED, WORKFLOW_STATUS_FAILED}:
        workflow.completed_at = datetime.datetime.utcnow()
    db.commit()


def create_generation_workflow(
    db: Session,
    req: GenerateWorkflowRequest,
) -> tuple[WorkflowExecution, AIJob]:
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise ValueError("project_id not found")

    workflow = WorkflowExecution(
        project_id=req.project_id,
        workflow_type="generate_video",
        status=WORKFLOW_STATUS_QUEUED,
        progress=0.0,
        input_payload=req.model_dump(),
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    job = AIJob(
        project_id=req.project_id,
        workflow_execution_id=workflow.id,
        status=JOB_STATUS_QUEUED,
        progress=0.0,
        model=req.model,
        prompt=req.prompt,
        image_path=req.image,
        steps=req.steps,
        guidance_scale=req.guidance_scale,
        seed=req.seed,
        size=req.size,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    emit_event(
        db,
        event_type="ai_job.submitted",
        domain="ai_gateway",
        entity_id=job.id,
        project_id=job.project_id,
        job_id=job.id,
        payload={
            "workflow_execution_id": workflow.id,
            "model": job.model,
            "size": job.size,
        },
    )

    return workflow, job


def _resolve_input_image(job: AIJob) -> str | None:
    if not job.image_path:
        return None

    raw = job.image_path.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if Path(raw).exists():
        return raw

    image_dir = Path(settings.OUTPUT_DIR) / "inputs"
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / f"{job.id}_input.png"

    try:
        decoded = base64.b64decode(raw)
        with open(image_path, "wb") as f:
            f.write(decoded)
        return str(image_path)
    except Exception:
        return raw


def _run_job(job_id: str) -> None:
    db = SessionLocal()
    worker = _get_worker()

    try:
        job = db.query(AIJob).filter(AIJob.id == job_id).first()
        if not job:
            return
        workflow = (
            db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == job.workflow_execution_id)
            .first()
        )
        if not workflow:
            return

        _transition_ai_job(db, job, JOB_STATUS_PROCESSING, progress=0.05)
        _transition_workflow(db, workflow, WORKFLOW_STATUS_PROCESSING, progress=0.05)

        emit_event(
            db,
            event_type="ai_job.started",
            domain="ai_gateway",
            entity_id=job.id,
            project_id=job.project_id,
            job_id=job.id,
            payload={"workflow_execution_id": workflow.id},
        )

        def _progress_update(value: float):
            latest_job = db.query(AIJob).filter(AIJob.id == job_id).first()
            latest_workflow = (
                db.query(WorkflowExecution)
                .filter(WorkflowExecution.id == workflow.id)
                .first()
            )
            if not latest_job or not latest_workflow:
                return
            latest_job.progress = min(max(value, 0.0), 1.0)
            latest_workflow.progress = latest_job.progress
            db.commit()

        output_dir = Path(settings.OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"{job.id}.mp4")

        image_path = _resolve_input_image(job)

        result_path = worker.generate(
            prompt=job.prompt,
            image_path=image_path,
            task=job.model,
            size=job.size,
            steps=job.steps,
            guidance=job.guidance_scale,
            seed=job.seed,
            output_path=output_path,
            progress_callback=_progress_update,
        )

        latest_job = db.query(AIJob).filter(AIJob.id == job_id).first()
        latest_workflow = (
            db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == workflow.id)
            .first()
        )

        if latest_job and latest_workflow:
            latest_job.output_path = result_path
            _transition_ai_job(db, latest_job, JOB_STATUS_COMPLETED, progress=1.0)
            _transition_workflow(db, latest_workflow, WORKFLOW_STATUS_COMPLETED, progress=1.0)

            emit_event(
                db,
                event_type="ai_job.completed",
                domain="ai_gateway",
                entity_id=latest_job.id,
                project_id=latest_job.project_id,
                job_id=latest_job.id,
                payload={
                    "workflow_execution_id": latest_workflow.id,
                    "output_path": latest_job.output_path,
                },
            )

            emit_event(
                db,
                event_type="project.updated",
                domain="projects",
                entity_id=latest_job.project_id,
                project_id=latest_job.project_id,
                job_id=latest_job.id,
                payload={"reason": "ai_job_completed"},
            )

    except Exception as exc:
        failed_job = db.query(AIJob).filter(AIJob.id == job_id).first()
        if failed_job:
            failed_workflow = (
                db.query(WorkflowExecution)
                .filter(WorkflowExecution.id == failed_job.workflow_execution_id)
                .first()
            )
            if failed_job.status in _ALLOWED_TRANSITIONS and JOB_STATUS_FAILED in _ALLOWED_TRANSITIONS[failed_job.status]:
                _transition_ai_job(db, failed_job, JOB_STATUS_FAILED, progress=0.0, error=str(exc))
            else:
                failed_job.error = str(exc)
                db.commit()

            if failed_workflow:
                _transition_workflow(db, failed_workflow, WORKFLOW_STATUS_FAILED, progress=0.0, error=str(exc))

            emit_event(
                db,
                event_type="ai_job.failed",
                domain="ai_gateway",
                entity_id=failed_job.id,
                project_id=failed_job.project_id,
                job_id=failed_job.id,
                payload={"error": str(exc)},
            )
    finally:
        db.close()


def start_generation_job(job_id: str) -> None:
    thread = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    thread.start()
