from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    project_id: str | None = None
    job_id: str | None = None
    event_type: str
    channel: str
    title: str
    message: str
    is_read: bool
    created_at: datetime
