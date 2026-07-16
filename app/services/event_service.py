from sqlalchemy.orm import Session

from app.models.event_log import EventLog


def emit_event(
    db: Session,
    *,
    event_type: str,
    domain: str,
    entity_id: str,
    project_id: str | None = None,
    job_id: str | None = None,
    payload: dict | None = None,
    commit: bool = True,
) -> EventLog:
    event = EventLog(
        event_type=event_type,
        domain=domain,
        entity_id=entity_id,
        project_id=project_id,
        job_id=job_id,
        payload=payload or {},
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    return event
