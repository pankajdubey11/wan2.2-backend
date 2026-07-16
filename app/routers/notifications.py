from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.services.notification_service import mark_notification_read

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    project_id: str | None = Query(default=None),
    only_unread: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(Notification)
    if project_id:
        query = query.filter(Notification.project_id == project_id)
    if only_unread:
        query = query.filter(Notification.is_read.is_(False))

    notifications = query.order_by(Notification.created_at.desc()).limit(100).all()
    return [
        NotificationResponse(
            id=n.id,
            project_id=n.project_id,
            job_id=n.job_id,
            event_type=n.event_type,
            channel=n.channel,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at,
        )
        for n in notifications
    ]


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def read_notification(notification_id: str, db: Session = Depends(get_db)):
    notification = mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse(
        id=notification.id,
        project_id=notification.project_id,
        job_id=notification.job_id,
        event_type=notification.event_type,
        channel=notification.channel,
        title=notification.title,
        message=notification.message,
        is_read=notification.is_read,
        created_at=notification.created_at,
    )
