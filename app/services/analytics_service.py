from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.ai_job import AIJob


def get_overview_metrics(db: Session, project_id: str | None = None) -> dict:
    query = db.query(AIJob)
    if project_id:
        query = query.filter(AIJob.project_id == project_id)

    total = query.count()
    completed = query.filter(AIJob.status == "completed").count()
    failed = query.filter(AIJob.status == "failed").count()
    queued = query.filter(AIJob.status == "queued").count()
    processing = query.filter(AIJob.status == "processing").count()

    completion_rate = (completed / total) if total else 0.0

    latency_query = db.query(
        func.avg(
            func.julianday(AIJob.completed_at) - func.julianday(AIJob.started_at)
        )
    ).filter(AIJob.started_at.is_not(None), AIJob.completed_at.is_not(None))
    if project_id:
        latency_query = latency_query.filter(AIJob.project_id == project_id)

    avg_days = latency_query.scalar() or 0.0
    avg_seconds = float(avg_days) * 86400.0

    return {
        "total_jobs": total,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "queued_jobs": queued,
        "processing_jobs": processing,
        "completion_rate": round(completion_rate, 4),
        "avg_latency_seconds": round(avg_seconds, 2),
    }


def get_model_usage(db: Session, project_id: str | None = None) -> list[dict]:
    base = db.query(
        AIJob.model.label("model"),
        func.count(AIJob.id).label("count"),
        func.sum(case((AIJob.status == "completed", 1), else_=0)).label("completed"),
        func.sum(case((AIJob.status == "failed", 1), else_=0)).label("failed"),
    )

    if project_id:
        base = base.filter(AIJob.project_id == project_id)

    rows = base.group_by(AIJob.model).order_by(func.count(AIJob.id).desc()).all()

    return [
        {
            "model": row.model,
            "count": int(row.count or 0),
            "completed": int(row.completed or 0),
            "failed": int(row.failed or 0),
        }
        for row in rows
    ]
