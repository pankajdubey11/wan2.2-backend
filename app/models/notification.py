import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, JSON, String, Text

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    job_id = Column(String, ForeignKey("ai_jobs.id"), nullable=True, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    channel = Column(String(32), nullable=False, default="in_app")
    title = Column(String(160), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
