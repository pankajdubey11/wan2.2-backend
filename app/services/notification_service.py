from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_in_app_notification(
    db: Session,
    *,
    project_id: str | None,
    job_id: str | None,
    event_type: str,
    title: str,
    message: str,
    payload: dict | None = None,
    commit: bool = True,
) -> Notification:
    notification = Notification(
        project_id=project_id,
        job_id=job_id,
        event_type=event_type,
        channel="in_app",
        title=title,
        message=message,
        payload=payload or {},
    )
    db.add(notification)
    if commit:
        db.commit()
        db.refresh(notification)
    return notification


def mark_notification_read(db: Session, notification_id: str) -> Notification | None:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
